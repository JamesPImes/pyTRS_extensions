# `pytrs_ext.pandas_tools` module
A few tools for expanding `pytrs` functionality to `pandas`.

*__Note:__ This package is NOT imported with `pytrs_ext` by default.*


#### `parse_plssdescs()`

Parse PLSS descriptions in a pandas `DataFrame` into Tracts (and into lots and QQs).

```
from pytrs_ext.pandas_tools import parse_plssdescs
 
# Create a DataFrame from a .csv file that has PLSS land descriptions in
# a column with the header 'land_desc'.
sample_df = pd.read_csv(r'C:\land\sample_land_descriptions.csv')

# Parse the PLSS descriptions into a new DataFrame, with rows added as 
# needed, such that there is one parsed tract per row. (`config=` is 
# optional.)
parsed_df = parse_plssdescs(
    sample_df, plss_col='land_desc', config='n,w,segment')

# Print the Twp/Rge/Sec, description block, lots, and quarter-quarters
# ('QQs') -- all as parsed by pyTRS.
print(parsed_df[['trs', 'desc', 'lots', 'qqs']])
```


#### `parse_tracts()`

Parsing tracts into lots and QQs.

A tract in this context means a description that has already been separated from its Twp/Rge/Sec. For example, `'Lots 1, 2, 3, S/2NE/4'` or `'S/2'` in `'Lots 1, 2, 3, S/2NE/4 of Section 1, S/2 of Section 2, T154N-R97W'`. (Many databases already have this data in separate columns.)

```
from pytrs_ext.pandas_tools import parse_tracts

# Create a DataFrame from a .csv file that has tract descriptions in a
# column with the header 'tract_desc'.
sample_df = pd.read_csv(r'C:\land\sample_land_descriptions.csv')

# Parse the tracts into lots and QQs into the same DataFrame. (`config=`
# is optional.)
parse_tracts(sample_df, tract_col='tract_desc', config='clean_qq')

# Print the lots and quarter-quarters ('QQs'), as parsed by pyTRS.
print(sample_df[['lots', 'qqs']])
```

#### `filter_by_trs()`

Filter a DataFrame by Twp/Rge/Sec (TRS) -- even if the PLSS land descriptions in the DataFrame contain multiple TRS's, and even if that data has not been parsed.

```
from pytrs_ext.pandas_tools import filter_by_trs

# Create a DataFrame from a .csv file with PLSS land descriptions in a
# column with the header 'land_desc'.
sample_df = pd.read_csv(r'C:\land\sample_land_descriptions.csv')


# To filter for a single Twp/Rge/Sec, pass `trs` as a string.
filtered_df_single = filter_by_trs(
    sample_df, plss_col='land_desc', trs='154n97w14')


# To filter for multiple TRS, pass a list as `trs`.
relevant_trs_list = ['154n97w14', '6s101e02']

# Filter the dataframe to those whose land descriptions include AT LEAST
# one of the TRS's in the list.
filtered_df_including = filter_by_trs(
    sample_df, plss_col='land_desc', trs=relevant_trs_list)

# Or use the `include=False` to filter for those descriptions that
# contain NONE of the Twp/Rge/Sec's passed in `trs`.
filtered_df_excluding = filter_by_trs(
    sample_df, plss_col='land_desc', trs=relevant_trs_list, include=False)
```

For this method, a match of __any__ TRS will count as a positive match, both for purposes of inclusive filter (`include=True`) and exclusive filter (`include=False`).


*__Note:__* TRS must be specified in the [standardized format used by pyTRS](https://github.com/JamesPImes/pyTRS/blob/master/guides/guides/trs.md#standard-pytrs-format-for-twprgesec), being a single string consisting of three parts:

| Component | Format                                                | Example       |
|-----------|-------------------------------------------------------|---------------|
| Township  | Up to three digits, plus `'n'` or `'s'` for direction | `T154N -> '154n'` <br> `T7S -> '7s'`|
| Range     | Up to three digits, plus `'e'` or `'w'` for direction | `R97W -> '97w'` <br> `R9E -> '9e'`|
| Section   | Exactly two digits                                    | `Section 14 -> '14'` <br> `Section 1 -> '01'`|

These are combined to form the `trs` in the standardized format:

* `Section 14 of T154N-R97W` becomes `'154n97w14'`
* `Section 1 of T7S-R9E` becomes `'7s9e01'`