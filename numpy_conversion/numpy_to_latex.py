import re
from numpy_array_from_string import split_brackets, is_not_stub_row, numregex, not_whitespace_rows

def numpy_to_latex(mat,bracket_type='b'):
	strmat = str(mat)
	begin = r"$\begin{"+bracket_type+"matrix}"+'\n'
	end_ = "\n"+r"\end{"+bracket_type + "matrix}$"
	out_rows = not_whitespace_rows(strmat)
	out_rows = [' & '.join(re.findall(numregex,row)) for row in out_rows]
	print(begin + ' \\\\ \n'.join(out_rows) + end_)
	