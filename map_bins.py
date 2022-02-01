'''Utilities for taking binned data where only the bins are known and mapping
the data into new bins.
'''
import numpy as np
import pandas as pd

def lowhigh_intersect_frac(low, high, new_low, new_high):
    if new_high == float('inf') and high == float('inf'):
        # inf - inf is nan
        return 1.0
    minhigh = min(new_high, high)
    maxlow = max(new_low, low)
    intersect_amt = max(0, minhigh - maxlow)
    if intersect_amt > 0:
        return intersect_amt/(high - low)
    
    return 0

def map_bins(old_bins, new_bins):
    '''old_bins, new_bins: lists of int or float, the starts of bins.
    len(new_bins) should be <= len(old_bins).
Returns: a map from old bin starts to lists of (new bin start, fraction) tuples
The end of each bin is assumed to be the start of the next bin, or float('inf')
    if there is no next bin.

EXAMPLES:
___________
>>> map_bins([0, 5, 10], [0, 10])
{0: [(0, 1.0)], 5: [(0, 1.0)], 10: [(10, 1.0)]}
>>> map_bins([0, 5, 10], [0, 4, 8])
{0: [(0, 0.8), (4, 0.2)], 5: [(4, 0.6), (8, 0.4)], 10: [(8, 1.0)]}
>>> # TODO: the above example demonstrates a potential flaw in this code. See about fixing it.
    '''
    assert len(new_bins) <= len(old_bins), f"Can't sensibly move the contents of {len(old_bins)} bins into {len(new_bins)} new bins." 
    lows = sorted(set(old_bins))
    highs = lows[1:]+[float('inf')]
    new_low_set = sorted(set(new_bins))
    new_high_set = new_low_set[1:] + [float('inf')]
    
    low_map = {}
    for low, high in zip(lows, highs):
        low_map.setdefault(low, [])
        lh_intersect = lambda l, h: lowhigh_intersect_frac(low, high, l, h)
        for newlow, newhigh in zip(new_low_set, new_high_set):
            intersect_frac = lh_intersect(newlow, newhigh)
            if intersect_frac > 0:
                low_map[low].append((newlow, intersect_frac))
    return low_map

def change_bins(df, low_bin_col, high_bin_col, New_lows, *numcols):
    old_lows = sorted(set(df[low_bin_col]))
    new_lows = sorted(set(New_lows))
    new_highs = new_lows[1:] + [float('inf')]
    bin_map = map_bins(df[low_bin_col], new_lows)
    len_per_bin = int(len(df)/len(old_lows))
    new_len = len_per_bin * len(new_lows)
    new_df = pd.DataFrame({col: np.zeros(new_len, dtype = df[col].dtype) \
                          for col in df.columns})
    
    new_low_slices = {}
    for ii, (new_low, new_high) in enumerate(zip(new_lows, new_highs)):
        new_low_slices[new_low] = slice(ii*len_per_bin, (ii+1)*len_per_bin-1)
    
    for old_low in old_lows:
        old_rows = df[df[low_bin_col] == old_low]
        for new_low, frac in bin_map[old_low]:
            new_slice = new_low_slices[new_low]
            # print(f'{old_low = },{old_rows.shape = }, {new_slice = }')
            new_high = new_highs[new_lows.index(new_low)]
            new_df.loc[new_slice, low_bin_col] = new_low
            new_df.loc[new_slice, high_bin_col] = new_high
            for col in df.columns:
                # print(f'{old_rows[col].values.shape = }, {old_rows[col].shape = }, {new_df.loc[new_slice, col].shape = }')
                if col in {low_bin_col, high_bin_col}:
                    continue
                elif col in numcols:
                    new_df.loc[new_slice, col] += old_rows[col].values * frac
                else:
                    new_df.loc[new_slice, col] = old_rows[col].values
    
    return new_df

def map_bins_test():
    bintest = pd.DataFrame({'low': [0, 0, 5, 5, 10, 10], 
                           'high': [5, 5, 10, 10, float('inf'), float('inf')],'a': ['a', 'b', 'a', 'b', 'a', 'b'], 
                           'population': [15, 30, 40, 35, 55, 20]})
    
    new_lows = [[0, 5],
            [0, 3, 6],
            [2, 7, 11]]
    correct_pops = [
                    (15, 30, 40+55, 35+20),
                    (15*0.6, 30*0.6, 
                       15*0.4+40*0.2, 30*0.4+35*0.2,
                       40*0.8+55, 35*0.8+20),
                    (15*0.6+40*0.4, 30*0.6+35*0.4,
                       40*0.6, 35*0.6,
                       55, 20)
                    ]
    failed = 0
    for lows, correct_pop in zip(new_lows, correct_pops):
        binmap1 = change_bins(bintest, 'low', 'high', lows, 'population')
        ans = tuple(binmap1.population)
        if ans != correct_pop:
            failed += 1
            print(f"didn't correctly map bins [0, 5, 10] to {lows}. Got {ans}, wanted {correct_pop}.")
    
    print(f"Failed {failed} out of {len(new_lows)} tests.")
    
if __name__ == '__main__':
    map_bins_test()