# Copyright (c) 2021, James P. Imes. All rights reserved.

"""
Misc. tools for extending pyTRS functionality to pandas.
"""

import pytrs
import pandas as pd


def parse_tracts(df: pd.DataFrame, tract_col: str, suffix="_parsed") -> pd.DataFrame:
    """
    Parse PLSS tracts in a pandas DataFrame, into lots and QQs.
    NOTE: May only use this if the description block is separated from
    its corresponding Township, Range, and Section -- with Twp/Rge/Sec
    in different column(s) from the column to be parsed by this
    function. (For more info on what constitutes a 'tract' as meant
    here, see docs on pytrs.Tract objects.)

    Returns the same DataFrame (columns added in-situ).

    :param df: a pandas DataFrame with a column that contains PLSS tract
    descriptions.
    :param tract_col: The header of the column containing PLSS tract
    descriptions to be parsed.
    :param suffix: The suffix to be added to the column headers (will
    only apply if the attempted headers already exist in the DataFrame).
    Defaults to "_parsed" (if needed at all).
    :return: The same DataFrame with added columns for the parsed PLSS
    data.
    """

    # List of attributes we want to extract from each pytrs.Tract object.
    atts = ["lots", "qqs", "w_flags", "e_flags"]

    # Headers for that data as will be written into the DataFrame
    headers = ["lots", "qqs", "warning_flags", "error_flags"]

    # Parse the tract in each row into a pytrs.Tract object, and extract
    # the relevant data to a list of dicts. Note that the attributes
    # being extracted here are all lists of strings (by design of pytrs).
    # So we'll eventually ", ".join() on them before writing them to the
    # DataFrame.
    parsed_tracts = [
        pytrs.Tract(row[tract_col], parse_qq=True).to_dict(atts)
        for _, row in df.iterrows()
    ]

    # Add a column for each parsed attribute.
    for header, att in zip(headers, atts):
        if header in df.columns:
            # If the header already exists in the DataFrame, we'll add
            # the suffix.
            header = f"{header}{suffix}"

        # Extract the relevant data for each tract and add it as a new column
        df[header] = [", ".join(dct[att]) for dct in parsed_tracts]

    return df


def parse_plssdescs(
        df: pd.DataFrame, plss_col: str, suffix="_parsed", config=None) -> pd.DataFrame:
    """
    Parse PLSS land descriptions in a pandas DataFrame, adding new rows
    as necessary. Returns a new DataFrame.
    WARNING: Will most likely result in a one-to-many merge (i.e. some
    rows may be duplicated).

    :param df: A pandas DataFrame with a column that contains PLSS land
    descriptions.
    :param plss_col: The header of the column containing PLSS land
    descriptions to be parsed.
    :param suffix: The suffix to add to the added column headers.
    :param config: (Optional) A pytrs.Config object or config parameters
    (see pytrs.Config docs for details).
    :return: A new DataFrame with added rows and columns for the parsed
    PLSS data.
    """

    # The attribute names of a pytrs.PLSSDesc object that are relevant
    # for our purposes.
    atts = [
        "source", "trs", "twp", "rge", "sec", "desc", "lots",
        "qqs", "w_flags", "e_flags"
    ]

    # The corresponding headers for that data, as will be written into
    # the DataFrame
    headers = [
        "ind", "trs", "twp", "rge", "sec", "desc", "lots", "qqs",
        "warning_flags", "error_flags"
    ]

    # These attributes are extracted as lists (which will be joined before
    # adding to the DataFrame).
    list_type_atts = ["lots", "qqs", "w_flags", "e_flags"]

    parsed_tracts = []
    for ind, row in df.iterrows():
        # Parse the PLSS description in this row. Specify `source=ind`
        # so that each parsed description knows the row it came from (so
        # we can `pd.merge()` on that column later).
        dsc = pytrs.PLSSDesc(
            row[plss_col], parse_qq=True, config=config, source=ind)

        # Extract the tract data into a list of dicts, and tack them onto
        # the end of parsed_descs
        parsed_tracts.extend(dsc.tracts_to_dict(atts))

    # Create a new DataFrame from the parsed data.
    ndf = pd.DataFrame()
    def same(x): return x
    def join(x): return ", ".join(x)
    for att, header in zip(atts, headers):
        func = same
        if att in list_type_atts:
            func = join
        ndf[header] = [func(dct[att]) for dct in parsed_tracts]

    # # Merge our original DataFrame to the new one, and return the result
    # return pd.merge(
    #     df, ndf, left_index=True, right_on="ind", suffixes=("", suffix))

    ndf = ndf.set_index("ind")

    # Merge our original DataFrame to the new one, and return the result
    return pd.merge(
        df, ndf, left_index=True, right_index=True, suffixes=("", suffix))


def filter_by_trs(
        df: pd.DataFrame, plss_col: str, trs, include=True, config=None) -> pd.DataFrame:
    """
    Filter a pandas DataFrame containing unparsed PLSS land descriptions
    to those rows that contain the specified Twp/Rge/Sec (TRS).
    Alternatively, filter rows to those that do NOT contain the
    specified TRS with `include=False` (set to True by default).
    Optionally pass multiple TRS's to match by passing a tuple of
    strings as `trs` (only one needs to match to qualify as a hit).

    :param df: A pandas DataFrame with a column that contains PLSS land
    descriptions.
    :param plss_col: The header of the column containing PLSS land
    descriptions to filter on.
    :param trs: A string, representing the TRS in question, in the
    pytrs format (i.e. '000n000w00', or fewer digits for Twp or Rge,
    if appropriate -- e.g., '154n97w14' or '8s22e01'). May also pass in
    a list or tuple of multiple TRS's, in which case only one TRS needs
    to match to qualify as a hit.
    :param include: Whether to filter to those results that include the
    specified TRS (`True`, the default behavior), or to exclude exclude
    (i.e. `False`).
    :param config: (Optional) A pytrs.Config object or config parameters
    (see pytrs.Config docs for details).
    :return: A filtered DataFrame.
    """
    if not include:
        return df[~df[plss_col].apply(plssdesc_contains_trs, args=(trs, config))]
    return df[df[plss_col].apply(plssdesc_contains_trs, args=(trs, config))]


def plssdesc_contains_trs(plssdesc_raw: str, trs, config=None) -> bool:
    """
    Whether the unparsed PLSS land description contains the specified
    township/range/section (TRS).

    :param plssdesc_raw: An unparsed PLSS land description (a string).
    :param trs: A string, representing the TRS in question, in the
    pytrs format (i.e. '000n000w00', or fewer digits for Twp or Rge,
    if appropriate -- e.g., '154n97w14' or '8s22e01'). May also pass in
    a list or tuple of multiple TRS's, in which case only one TRS needs
    to match to qualify as a hit.
    :param config: (Optional) A pytrs.Config object or config parameters
    (see pytrs.Config docs for details).
    :return: A bool, whether or not the TRS is found in the PLSS
    description.
    """
    if isinstance(trs, (pytrs.TRS, str)):
        # If a single object was passed, put it in a list.
        trs = [trs]
    # Use str() to convert any pytrs.TRS objects in the list.
    sought_trs = set([str(t).lower() for t in trs])
    dsc = pytrs.PLSSDesc(plssdesc_raw, parse_qq=True, config=config)
    found_trs = set(dsc.list_trs())
    return len(sought_trs.intersection(found_trs)) > 0


__all__ = [
    parse_tracts,
    parse_plssdescs,
    filter_by_trs,
    plssdesc_contains_trs
]
