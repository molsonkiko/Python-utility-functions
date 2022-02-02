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
    '''
    numranges = {}
    others = {}
    min_low = INF
    for s in ranges:
        nums = re.findall(num_money_regex, s)
        if nums:
            # print(f'{nums = }, {min_low = }, {min_low_keys = }')
            n1 = float(re.sub('\D', '', nums[0]))
            if len(nums) == 2:
                n2 = float(re.sub('\D', '', nums[1]))
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
    '''
    return dict(zip(ranges.keys(), fix_bins(ranges.values(), default_min).values()))
    
def rangestring_col(df, low_colname, high_colname, zfill = True):
    if zfill:
        import numpy as np
        uniques = np.concatenate((df[high_colname].unique(),
                                  df[low_colname].unique()))
        num_zs = max(len(str(int(x))) for x in uniques[uniques < INF])
        lowcol = df[low_colname].astype(int).astype(str).str.zfill(num_zs)
        highcol = df[high_colname].astype(str) \
                                  .str.replace('.0', '', regex = False) \
                                  .str.zfill(num_zs)
    else:
        lowcol = df[low_colname].astype(int).astype(str)
        highcol = df[high_colname].astype(str) \
                                  .str.replace('.0', '', regex = False) 
    return (lowcol + '-' + highcol).str.replace('-inf', '+', regex = False)

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