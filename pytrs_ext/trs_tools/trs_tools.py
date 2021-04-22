# Copyright (c) 2021, James P. Imes. All rights reserved.

"""
Functions for identifying Twp/Rge/Sec using regex patterns for
'non-standard' formats.
"""

import re
import pytrs

# ----------------------------------------------------------------------
# Some preset formats for the `custom_trs_list()` function.

# For unpacking in the format '154n97w - 1, 14, 15, 36, 155n97w - 23, 1'
FORMAT_A = {
    'rgx': re.compile(
        r"(?P<twp>\d{1,3}[NSns])(?P<rge>\d{1,3}[EWew]) - "
        r"(?P<sec_list>(\d{1,2}(, )?(?!\d{1,3}[NSns]))+)"),
    'sec_key': lambda sec_list: sec_list.split(', '),
}

# For unpacking in the format '154-097-014-001' -- i.e. '154n97w14' and
# '154n97w01'
FORMAT_B = {
    'rgx': re.compile(
        r"(?P<twp>\d{1,3})-(?P<rge>\d{1,3})-(?P<sec_list>(\d{1,3}-?)+)"),
    'sec_key': lambda sec_list: [int(sec) for sec in sec_list.split('-')],
}

# For unpacking in the format '014-001-154-097' -- i.e. '154n97w14' and
# '154n97w01'.  Or '014-154-097' for '154n97w14'.  (Any positive number
# of sections, so long as Twp/Rge come last.)
FORMAT_C = {
    'rgx': re.compile(
        r"(?P<sec_list>(\d{1,3}-?)+)-(?P<twp>\d{1,3})-(?P<rge>\d{1,3})"),
    'sec_key': lambda sec_list: [int(sec) for sec in sec_list.split('-')],
}

# Examples of input/output for the preset formats.
FORMAT_EXAMPLES = {
    'FORMAT_A': (
        '154n97w - 14, 1, 155n98w - 11',
        ['154n97w14', '154n97w01', '155n98w11']
    ),
    'FORMAT_B': (
        '154-097-014-001',
        ['154n97w14', '154n97w01']
    ),
    'FORMAT_C': (
        '014-154-097',
        ['154n97w14']
    )
}
# ----------------------------------------------------------------------


def custom_trs(txt, rgx, default_ns=None, default_ew=None):
    r"""
    Get a `pytrs.TRS` object from a string (`txt`), using a custom regex
    pattern `rgx`. The `rgx` pattern should have named groups 'twp',
    'rge', and 'sec', each of which match to values that can be passed
    as `twp=`, `rge=`, and `sec=` in the `pytrs.TRS.from_twprgesec()`
    method.

    Example regex, to match '154-097-014' as `'154n97w14':
        r"(?P<twp>\d{3})-(?P<rge>\d{3})-0(?P<sec>\d{2})"
    (Note that in this example, a '0' is placed outside of the 'sec'
    group in order to match only the rightmost 2 digits, because
    `.from_twprgesec()` requires that 'sec' be a maximum of 2 digits.)

    :param txt: The text from which to extract a pytrs.TRS object.

    :param rgx: A regex pattern with groups 'twp', 'rge', and 'sec'.
    Pass as either a string or a `re.Pattern` object.

    :param default_ns: Same purpose as in the pytrs library.

    :param default_ew: Same purpose as in the pytrs library.

    :return: A pytrs.TRS object. If unsuccessful and `txt` was not an
    empty string, will return the 'error' version of a pytrs.TRS object.
    If `txt` was an empty string, will return the 'undefined' version of
    a pytrs.TRS object.
    """
    mo = re.search(rgx, txt)
    if mo is None:
        return pytrs.TRS(txt)
    groups = mo.groupdict()
    return pytrs.TRS.from_twprgesec(
        twp=groups['twp'],
        rge=groups['rge'],
        sec=groups['sec'],
        default_ns=default_ns,
        default_ew=default_ew)


def custom_trs_list(txt, rgx, sec_key, default_ns=None, default_ew=None):
    r"""
    Get a `TRSList` of `pytrs.TRS` objects from a string (`txt`), using
    a custom regex pattern `rgx`. The `rgx` pattern should have named
    groups 'twp', 'rge', and 'sec_list'.  The match values of 'twp' and
    'rge' should be able to be passed to args `twp=` and `rge=` in the
    `pytrs.TRS.from_twprgesec()` method.

    However, 'sec_list' should match a string that can be broken down
    into one or more section numbers.  You must also pass `sec_key`, a
    function that will apply to the matched 'sec_list' string(s) in
    order to break it down into a list of strings or integers (each of
    which is 1 or 2 digits long).

    Example `rgx` and `sec_key`, to match and parse '154-097-014-001' as
    `['154n97w14', '154n97w01']`:

    >>> text = '154-097-014-001'
    >>> pat = r"(?P<twp>\d{3})-(?P<rge>\d{3})-(?P<sec_list>(\d{3}-?)+)"
    >>> key = lambda sl_group: [int(sec) for sec in sl_group.split('-')]
    >>> trs_list = custom_trs_list(txt=text, rgx=pat, sec_key=key)


    Note: Several presets for common formats have been provided. These
    are dicts whose keys line up with parameters for this function. You
    can use one of the presets provided in this module like so:

    >>> text1 = '154n97w - 14, 01'
    >>> trs_list1 = custom_trs_list(txt=text1, **FORMAT_A)

    or more explicitly...

    >>> trs_list1 = custom_trs_list(
    ...     txt=text1, rgx=FORMAT_A['rgx'], sec_key=FORMAT_A['sec_key'])

    >>> text2 = '154-097-014-001'
    >>> trs_list2 = custom_trs_list(txt=text2, **FORMAT_B)

    (See the available presets in the ``FORMAT_EXAMPLES`` dict.)


    :param txt: The text from which to extract a TRS object.

    :param rgx: A regex pattern with groups 'twp', 'rge', and
    'sec_list'.  Pass as either a string or a `re.Pattern` object.

    :param sec_key: A function that takes as input a string that encodes
    one or more section numbers (e.g., the 'sec_list' match group from
    the regex pattern passed as `rgx`) and returns a list of strings
    (each string being 1 or 2 numerical chars).  For example, a function
    that breaks `'001-002-005'` into `['1', '2', '5']`:
        `lambda string: [sec.lstrip('0') for sec in string.split('-')]`

    :param default_ns: Same purpose as in the pytrs library.

    :param default_ew: Same purpose as in the pytrs library.

    :return: A `TRSList` of `pytrs.TRS` objects.
    """
    rgx = re.compile(rgx)
    trs_list = pytrs.TRSList()
    for mo in re.finditer(rgx, txt):
        groups = mo.groupdict()
        twp = groups['twp']
        rge = groups['rge']
        sec_list = groups['sec_list']
        sec_list = sec_key(sec_list)
        new = [
            pytrs.TRS.from_twprgesec(twp, rge, sec, default_ns, default_ew)
            for sec in sec_list
        ]
        trs_list.extend(new)
    return trs_list


def trs_list_to_format_a(
        trs_list, sec_delimiter=', ', twprge_delimiter=', ',
        discard_errors=False) -> str:
    """
    Convert a list of Twp/Rge/Sec's (either strings or pytrs.TRS
    objects) into a string in the predefined format `FORMAT_A`.

    For example, `['154n97w14', '154n97w01', '155n98w11']` will become
    `'154n97w - 14, 1, 155n98w - 11'`.

    :param trs_list: A list of Twp/Rge/Sec's, each being a pytrs.TRS
    object or an equivalent string. (May also be a `TRSList` object.)

    :param sec_delimiter: String to separate sections from one another.

    :param twprge_delimiter: String with which to separate one Twp/Rge
    and its sections from the next Twp/Rge.

    :param discard_errors: A bool, whether to throw out errors.

    :return: The compiled string.
    """
    ordered = []
    trs_list = pytrs.TRSList(trs_list)
    if discard_errors:
        trs_list.filter_errors(drop=True, undef=True)
    for trs in trs_list:
        if trs.twprge not in ordered:
            ordered.append(trs.twprge)
    grouped = trs_list.group(by_attribute='twprge')
    twprge_dct = {}
    for twprge, trslist in grouped.items():
        twprge_dct[twprge] = [trs.sec for trs in trslist]
    components = [
        f"{twprge} - {sec_delimiter.join(twprge_dct[twprge])}"
        for twprge in ordered
    ]
    return twprge_delimiter.join(components)


__all__ = [
    custom_trs,
    custom_trs_list,
    trs_list_to_format_a,
    FORMAT_A,
    FORMAT_B,
    FORMAT_C,
    FORMAT_EXAMPLES
]
