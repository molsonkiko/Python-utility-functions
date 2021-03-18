import re
#import pandas as pd
from numpy_array_from_string import is_not_stub_row, not_whitespace_rows

mymat = [
['''q" 'fubar''',"bju'fu, \"boy\" ]say", '"hey^{34} _{b}ab"','','$1.23'],
[     '', '1&3', '2' ,'7','-$9']]
# strupid_df = pd.DataFrame(mymat,index=['''djl' fjr"ew''',"jdfer's un"],
#                                           columns = ['a','b','c','d','e'])

#this is the most pathological dataframe I could think of. If someone else can think of
#something more horrible (from the perspective of pandas_to_latex), please try it

listitem_regex = '''[\[ ][\\'"](.*?)[\\'"][\],]'''
#finds anything preceded by a "[" or whitespace then a quotation mark
#and followed by a quotation mark and then a comma or "]"

def numpy_to_latex(mat,bracket_type='b'):
    strmat = re.sub('inf',r'\\infty',str(mat))
    strmat = re.sub('(\D)(\.\d+)','\g<1>0\g<2>',strmat)
    begin = r"$\begin{"+bracket_type+"matrix}"+'\n'
    end_ = "\n"+r"\end{"+bracket_type + "matrix}$"
    out_rows = not_whitespace_rows(strmat)
    out_rows = [' & '.join(re.split(',?\s+',row)) for row in out_rows]
    return begin + ' \\\\ \n'.join(out_rows) + end_
    
def pandas_to_latex(dataframe,bracket_type = ''):
    '''Converts a pandas DataFrame into a LaTeX matrix.
Replaces each individual blankspace inside individual entries of the DataFrame
with a single broad space character '\;'.
    Escapes "}","{","&", and "_", but not "^".
bracket_type: controls the type of bracket used to enclose the matrix.
    '''
    import numpy as np
    columns = list(dataframe.columns)
    index = list(dataframe.index)
    mat = dataframe.to_numpy(dtype = np.str_)
    if not index == list(range(len(dataframe))):
        mat_with_index = np.vstack([index] + [col for col in mat.T]).T
        mat_with_columns = np.vstack([['']+columns]+[row for row in mat_with_index])
    else:
        mat_with_columns = np.vstack([columns]+[row for row in mat])
    list_mat = [list(row) for row in mat_with_columns]
    
    for ii in range(len(list_mat)):
        for jj in range(len(list_mat[ii])): #make placeholders for whitespaces
            list_mat[ii][jj] = re.sub("\s",'~@~~',str(list_mat[ii][jj])) 
    strmat = ''
    for row in list_mat:
        strmat += '\t \t '.join(re.findall(listitem_regex,str(row)))+"\n"
    
    strmat = re.sub(':',r'\!:\!',strmat) #reduce space before and after colons
    strmat = re.sub('inf',r'\\infty',strmat)
    strmat = re.sub("(&|{|}|_|\$)","\\\\\g<1>",strmat) #escape '&','{', '_', '}' b/c special chars
    strmat = re.sub('(\D)(\.\d+)','\g<1>0\g<2>',strmat) #add 0 before numbers <1 w/o leading 0
    strmat = re.sub(r"\\'","'",strmat) #remove unneeded escapes (cause errors in LaTeX)
    begin = r"$\begin{"+bracket_type+"matrix}"+'\n'
    end_ = "\n"+r"\end{"+bracket_type + "matrix}$"
    out_rows = list(filter(not_whitespace_rows,strmat.split('\n'))) #get only good rows
    out_rows = [' & '.join(row.split("\t \t ")) for row in out_rows]
    for ii in range(len(out_rows)):
        out_rows[ii] = re.sub('~@~~',r'\\;',out_rows[ii]) #fill in whitespaces
    return begin + ' \\\\ \n'.join(out_rows) + end_
