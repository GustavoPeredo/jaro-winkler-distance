import math

__all__ = ['get_jaro_distance']
__author__ = 'Jean-Bernard Ratte - jean.bernard.ratte@unary.ca'

""" Find the Jaro Winkler Distance which indicates the similarity score between two Strings.
    The Jaro measure is the weighted sum of percentage of matched characters from each file and transposed characters.
    Winkler increased this measure for matching initial characters.

    This implementation is based on the Jaro Winkler similarity algorithm from
    http://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance

    This Python implementation is based on the Apache StringUtils implementation from
    http://commons.apache.org/proper/commons-lang/apidocs/src-html/org/apache/commons/lang3/StringUtils.html#line.7141
"""


def get_jaro_distance(first, second, winkler=True, winkler_ajustment=True, scaling=0.1):
    """
    :param first: word to calculate distance for
    :param second: word to calculate distance with
    :param winkler: same as winkler_ajustment
    :param winkler_ajustment: add an adjustment factor to the Jaro of the distance
    :param scaling: scaling factor for the Winkler adjustment
    :return: Jaro distance adjusted (or not)
    """
    if not first or not second:
        raise JaroDistanceException("Cannot calculate distance from NoneType ({0}, {1})".format(
            first.__class__.__name__,
            second.__class__.__name__))

    jaro = _score(first, second)
    cl = min(len(_get_prefix(first, second)), 4)

    if all([winkler, winkler_ajustment]):  # 0.1 as scaling factor
        return round((jaro + (scaling * cl * (1.0 - jaro))) * 100.0) / 100.0

    return jaro


def get_jaro_distance_array(first, second, winkler=True, winkler_ajustment=True, scaling=0.1):
    """
    :param first: word to calculate distance for
    :param second: list of words to calculate the distance with
    :param winkler: same as winkler_ajustment
    :param winkler_ajustment: add an adjustment factor to the Jaro of the distance
    :param scaling: scaling factor for the Winkler adjustment
    :return: list of Jaro distances adjusted (or not)
    """
    if not isinstance(second, list):
        second = [second]
    return [get_jaro_distance(first, i, winkler, winkler_ajustment, scaling) for i in second]


def _score(first, second):
    shorter, longer = first.lower(), second.lower()

    if len(first) > len(second):
        longer, shorter = shorter, longer

    m1 = _get_matching_characters(shorter, longer)
    m2 = _get_matching_characters(longer, shorter)

    if len(m1) == 0 or len(m2) == 0:
        return 0.0

    return ((float(len(m1)) / len(shorter) + float(len(m2))
            / len(longer) + float(len(m1) - _transpositions(m1, m2))
            / len(m1)) / 3.0)


def _get_diff_index(first, second):
    if first == second:
        return -1

    if not first or not second:
        return 0

    max_len = min(len(first), len(second))
    for i in range(0, max_len):
        if not first[i] == second[i]:
            return i

    return max_len


def _get_prefix(first, second):
    if not first or not second:
        return ""

    index = _get_diff_index(first, second)
    if index == -1:
        return first

    elif index == 0:
        return ""

    else:
        return first[0:index]


def _get_matching_characters(first, second):
    common = []
    limit = math.floor(min(len(first), len(second)) / 2)

    for i, l in enumerate(first):
        left, right = int(max(0, i - limit)), int(min(i + limit + 1, len(second)))
        if l in second[left:right]:
            common.append(l)
            second = second[0:second.index(l)] + '*' + second[second.index(l) + 1:]

    return ''.join(common)


def _transpositions(first, second):
    return math.floor(len([(f, s) for f, s in zip(first, second) if not f == s]) / 2.0)


class JaroDistanceException(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)
