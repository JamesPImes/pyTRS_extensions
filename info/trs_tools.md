
# `pytrs_ext.trs_tools` package

For identifying Twp/Rge/Sec and compiling `pytrs.TRS` objects using custom regex patterns.

*__Note:__ This package is automatically imported with `pytrs_ext`.*


### `trs_tools.custom_trs()`

Use this function to unpack a single `pytrs.TRS` object from a string using a custom regex. The regex must contain named groups `'twp'`, `'rge'`, and `'sec'`, whose matched strings will be passed to the correspondingly named argument in `pytrs.TRS.from_twprgesec(twp=<...>, rge=<...>, sec=<...>)`.

```
from pytrs_ext import trs_tools

found_trs = trs_tools.custom_trs(
    txt='154-097-014',
    rgx=r"(?P<twp>\d{3})-(?P<rge>\d{3})-0(?P<sec>\d{2})",
    default_ns='n',
    default_ew='w')

print(type(found_trs))
print(found_trs.twprge)
print(found_trs.sec)
```
The above example prints:
```
<class 'pytrs.parser.parser.TRS'>
154n97w
14
```

### `trs_tools.custom_trs_list()`

Use this function to extract a *__list__* of `pytrs.TRS` objects from text using a custom regex. The regex must contain named groups `'twp'`, `'rge'`, and (unlike the other function) `'sec_list'`.  Only the `'twp'` and `'rge'` matched strings will be passed directly to the correspondingly named argument in `pytrs.TRS.from_twprgesec(twp=<...>, rge=<...>)`.

However, the `'sec_list'` matched string will first be unpacked into a list of strings using the function passed as the `sec_key` argument.  `sec_key` should be a function that takes as input the `'sec_list'` match group and returns a list of strings (each string being 1 or 2 numerical chars).

In the following example, we define the function `key` to split the string and strip all leading `0`'s from each resulting section string, returning a list `['14', '1']`. And we pass that function as the `sec_key` argument.

```
from pytrs_ext import trs_tools

text = '154-097-014-001'
pattern = r"(?P<twp>\d{3})-(?P<rge>\d{3})-(?P<sec_list>(\d{3}-?)+)"

def key(sec_list_match_group):
    cleaned_list = []
    for sec in sec_list_match_group.split('-'):
        sec = sec.lstrip('0')
        cleaned_list.append(sec)
    return cleaned_list

trs_list = trs_tools.custom_trs_list(
    txt=text,
    rgx=pattern,
    sec_key=key)

for trs_object in trs_list:
    print(trs_object.trs)
```
The above example prints:
```
154n97w14
154n97w01
```

Note that the `sec_key` in the above example could have been passed as an equivalent `lambda`:

```
trs_list = trs_tools.custom_trs_list(
    txt=text,
    rgx=pattern,
    sec_key=lambda sl_group: [sec.lstrip('0') for sec in sl_group.split('-')]
)
```

#### Optional predefined formats for `custom_trs_list()`

A handful of predefined formats have been provided, and they can be used by passing them as a kwarg dict in place of the `rgx` and `sec_key` arguments.

```
from pytrs_ext import trs_tools

trs_list = trs_tools.custom_trs_list(
    txt='154n97w - 14, 1, 155n98w - 11', **trs_tools.FORMAT_A)

# Equivalently / more explicitly...
trs_list = trs_tools.custom_trs_list(
    txt='154n97w - 14, 1, 155n98w - 11',
    rgx=trs_tools.FORMAT_A['rgx'],
    sec_key=trs_tools.FORMAT_A['sec_key'])

for trs_object in trs_list:
    print(trs_object.trs)
```

The above example prints:
```
154n97w14
154n97w01
155n98w11
```

These are the provided presets:

| Format | Example Input | Example Output |
| --- | ----- | ------ |
`FORMAT_A` |  `'154n97w - 14, 1, 155n98w - 11'` |  `['154n97w14', '154n97w01', '155n98w11']` |
`FORMAT_B` | `'154-097-014-001'` | `['154n97w14', '154n97w01']` |
`FORMAT_C` | `'014-154-097'` | `['154n97w14']` |

*__Note:__ Do __NOT__ attempt to use these formats with `trs_tools.custom_trs()` -- use ONLY with `trs_tools.custom_trs_list()`.*
