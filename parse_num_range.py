'''Utilities for parsing iterables containing strings representing ranges of 
numbers as those ranges.
For example, ['Less than $1.50', '$1.50-$4.50', 'over 4.5 dollars'] could be
correctly parsed as [[0., 1.5], [1.5, 4.5], [4.5, 10.]] by fix_bins.
Also contains utilities for using this function on pandas DataFrames and dicts.
'''
import re

INF = float('inf')

num_money_regex = r'\$?((?:\d[_,]?)*\d\.?(?:\d(?:[_,]?\d)*)?(?:e[+-]?(?:\d[_,]?)*\d)?)'
# the num_money_regex matches positive numbers with scientific notation and 
# optional internal commas and underscores and an optional leading dollar sign

num_range_regex = f'^{num_money_regex}\D+{num_money_regex}$'


def fix_bins(ranges, default_min = -INF):
    '''Given an iterable containing strings,
    returns a dict mapping each original string to corresponding values 
    representing ranges (e.g., '1 to 5', '$1,000-$5,000')
    converted to 2-lists of floats (e.g. [1.0, 5.0], [1e4, 5e4]).
    Other strings are left as is.
EXAMPLES:
_______________
>>> fix_bins(['1 to 5.5 dollars', '$5.50-$1,000', '$1,000-$5,000'])
{'1 to 5.5 dollars': [1.0, 5.5], '$5.50-$1,000': [5.5, 1000.0], '$1,000-$5,000': [1000.0, 5000.0]}
>>> fix_bins(['Less than 2', '2-15', '15 up'], 0)
{'2-15': [2.0, 15.0], 'Less than 2': [0, 2.0], '15 up': [15.0, inf]}
>>> fix_bins(['foo', 'bar', 'baz', 'qux-1', '1-zubj'], -5)
{'qux-1': [-5, 1.0], '1-zubj': [1.0, inf], 'foo': 'foo', 'bar': 'bar', 'baz': 'baz'}
>>> fix_bins(['$15-$45'])
{'$15-$45': [15.0, 45.0]}
>>> fix_bins([])
{}
>>> fix_bins(['Under 1 year', '1', '1-15', '15 yo', '16+']) # fix_bins automatically fills gaps between one low and the next low, so it recognizes that '1' covers only the number 1, and '15 yo' covers [15, 16] because the next low is 16
{'1-15': [1.0, 15.0], 'Under 1 year': [-inf, 1.0], '1': [1.0, 15.0], '15 yo': [15.0, 16.0], '16+': [16.0, inf]}
    '''
    numranges = {}
    others = {}
    min_low = INF
    for s in ranges:
        nums = re.findall(num_money_regex, s)
        if nums:
            # print(f'{nums = }, {min_low = }, {min_low_keys = }')
            n1 = float(re.sub('[,\$_]', '', nums[0]))
            if len(nums) == 2:
                n2 = float(re.sub('[,\$_]', '', nums[1]))
                numranges[s] = [n1, n2]
            else:
                numranges[s] = [n1, INF]
        else:
            others[s] = s
    # print(f'{min_low = }, {min_low_keys = }')
    # in the above logic we assumed that if there's one number in the string,
    # that's the highest low.
    # But a one-number string could denote a single number, or a range from
    # n to n+1, or the lowest high. So we check to see if it's one of those.
    snums = sorted([list(it) for it in numranges.items()], key = lambda x: x[1])
    lows = [x[1][0] for x in snums]
    fixed_lowest_low = False
    for ii, (s,(lo, hi)) in enumerate(snums[:-1]):
        if hi == INF:
            if (not fixed_lowest_low) and lo == lows[0]:
                fixed_lowest_low = True
                snums[ii][1] = [default_min, lo]
            else:
                snums[ii][1] = [lo, lows[ii+1]]
    
    out = {**dict(snums), **others}
    
    return out

    
def fix_bin_dict(ranges, default_min = -INF):
    '''Given a dict mapping anything to strings, return a new dict where
    fix_bins was applied to the values.
EXAMPLES:
_______________
>>> fix_bin_dict({'a': 'Under 1 year', 'b': '1', 'c': '1-15', 'd': '15 yo', 'e': '16+'}, 0)
{'a': [1.0, 15.0], 'b': [0, 1.0], 'c': [1.0, 15.0], 'd': [15.0, 16.0], 'e': [16.0, inf]}
    '''
    return dict(zip(ranges.keys(), fix_bins(ranges.values(), default_min).values()))


def rangestring_col(df, low_colname, high_colname, zfill = True):
    '''Makes a pandas Series stringjoining df[low_colname] + '-' + def[high_colname].
Suitable if low_colname and high_colname represent the low and high ends of
ranges made by add_range_cols.
df: pandas.DataFrame.
low_colname, high_colname: int or str (valid types for df column name).
zfill: bool.
    '''
    if zfill:
        import numpy as np
        uniques = np.concatenate((df[high_colname].unique(),
                                  df[low_colname].unique()))
        num_zs = max(len(str(int(x))) for x in uniques[uniques < INF])
        lowcol = df[low_colname].astype(str) \
                                .str.replace('.0', '', regex = False) \
                                .str.zfill(num_zs)
        highcol = df[high_colname].astype(str) \
                                  .str.replace('.0', '', regex = False) \
                                  .str.zfill(num_zs)
    else:
        lowcol = df[low_colname].astype(str) \
                                .str.replace('.0', '', regex = False)
        highcol = df[high_colname].astype(str) \
                                  .str.replace('.0', '', regex = False) 
    
    return (lowcol + '-' + highcol) \
                .str.replace('-0*inf', '+', regex = True) \
                .str.replace('.*nan.*', 'Missing', regex = True)


def add_range_cols(df, col, low_colname = None, high_colname = None, default_min = -INF):
    '''Given a pandas DataFrame df and a column name col corresponding to
    ranges, add two columns, one with the low end of the bins made by fix_bins,
    and the other with the high end of the bins made by fix_bins.
    Also add a column representing the range from the low end of each bin to
    the high end as a string.
    Also delete df[col].'''
    if low_colname is None:
        low_colname = col + '_low'
    if high_colname is None:
        high_colname = col + '_high'
    
    range_strs = list(set(df[col]))
    ranges = fix_bins(range_strs, default_min)
    for s,rng in ranges.items():
        if not isinstance(rng, list):
            ranges[s] = [rng, float('nan')]
    df[col] = df[col].map(ranges)
    df[low_colname] = df[col].apply(lambda x: x[0])
    df[high_colname] = df[col].apply(lambda x: x[1])
    
    del df[col]
    
    
def test_parse_num_range():
    import doctest
    doctest.testmod()
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        print('pandas and numpy must be installed to run all tests for parse_num_range')
        return
    
    df = pd.DataFrame({
        'a': ['Under 1', '1 to 5.5 dollars', '$5.50-$1,000', '$1,000-$5,000'],
        'b': list('abcd')
    })
    dfc = df.copy()
    
    add_range_cols(dfc, 'a', 'alo', 'ahi', 0)
    expected_out = pd.DataFrame({'b': list('abcd'),
        'alo': [0, 1, 5.5, 1000.],
        'ahi': [1, 5.5, 1000., 5000.]})
    assert np.all(dfc == expected_out), \
        f"Given dfc =\n{dfc}\nexpected add_range_cols(dfc, 'a', 'alo', 'ahi', 0) to equal\n{expected_out},\ngot\n{dfc}"
        
    rsc_zf = rangestring_col(dfc, 'alo', 'ahi')
    expected_zf_out = pd.Series(['0000-0001', '0001-05.5', '05.5-1000', '1000-5000'])
    assert np.all(rsc_zf == expected_zf_out), \
        f'Given dfc =\n{dfc}\nexpected rangestring_col(dfc, "alo", "ahi", True) to return\n{expected_zf_out}\ngot\n{rsc_zf}'
    
    rsc = rangestring_col(dfc, 'alo', 'ahi', False)
    expected_rsc_out = pd.Series(['0-1', '1-5.5', '5.5-1000', '1000-5000'])
    assert np.all(rsc == expected_rsc_out), \
        f'Given dfc =\n{dfc}\nexpected rangestring_col(dfc, "alo", "ahi", False) to return\n{expected_rsc_out}\ngot\n{rsc}'
        
    

if __name__ == '__main__':
    test_parse_num_range()