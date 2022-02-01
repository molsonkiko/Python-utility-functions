import pandas as pd
import numpy as np
from collections import deque
import time

def is_empty(val):
	if (not val) and val != False:
		return True
	try:
		return np.isnan(val)
	except TypeError:
		return False
	
def is_empty_series(ser):
	return ser.apply(is_empty)
    
def split_by_empty(df, by = 'columns'):
    if isinstance(df, pd.Series):
        if not np.all(is_empty_series(df)):
            return [df] # don't cut out empty values of a 1d array
            
        return []
    empty_cells = df.apply(is_empty_series)
    sub_dfs = []
    new_df_dict = {}
    if by == 'columns':
        for col in df.columns:
            if np.all(empty_cells[col]):
                if new_df_dict:
                    sub_dfs.append(pd.DataFrame(new_df_dict))
                new_df_dict = {}
            else:
                new_df_dict[col] = df[col].copy()
        if new_df_dict:
            sub_dfs.append(pd.DataFrame(new_df_dict))
    else:
        for ind in df.index:
            if np.all(empty_cells.loc[ind]):
                if new_df_dict:
                    sub_dfs.append(pd.DataFrame(new_df_dict).T)
                new_df_dict = {}
            else:
                new_df_dict[ind] = df.loc[ind].copy()
        if new_df_dict:
            sub_dfs.append(pd.DataFrame(new_df_dict).T)
    
    return sub_dfs
    
def split_into_subframes(df):
    '''find blocks where no full row or column is empty, and make a list of 
    each subframe.
Do this recursively until you find 2d arrays with no fully
    missing rows and columns, or 1d arrays.'''
    to_split = deque([df])
    sub_dfs = []
    while to_split:
        the_df = to_split.popleft()
        by_rows = split_by_empty(the_df, 'rows')
        if len(by_rows) > 1:
            to_split.extend(by_rows)
        else:
            by_cols = split_by_empty(the_df)
            if len(by_cols) > 1:
                to_split.extend(by_cols)
            else:
                sub_dfs.append(the_df)
    
    return sub_dfs

if __name__ == '__main__':
    the_df = pd.DataFrame({
        'zero': {'a': '', 'b': '', 'c': np.nan, 'd': '', 'e': ''},
        'one': {'a': 'A', 'b': '', 'c': np.nan, 'd': 'd', 'e': 'E'},
        'two': {'a': None, 'b': '', 'c': np.nan, 'd': [], 'e': ''},
        'three': {'a': 'A', 'b': '', 'c': False, 'd': 'd', 'e': 'E'},
    })
    
    sub_the_df = split_into_subframes(the_df)
    '''sub_the_df should be divided into
[  one
 a   A,
   three
 a     A,
    one
 c  NaN
 d    d
 e    E,
    three
 c  False
 d      d
 e      E]'''