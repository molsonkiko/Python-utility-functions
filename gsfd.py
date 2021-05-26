'''

grep: a semi-functional workalike of the grep function in Linux for finding regex and
	other strings in files.
'''
import re, os, string

def is_iterable(x):
	'''returns False for strings, True for all other iterables'''
	return hasattr(x,'__iter__') and not isinstance(x,str)

def fname_checker(fname,ext):
	ext_begin = -len(fname)
	for ind in range(1,len(fname)+1):
		if fname[-ind]=='.':
			ext_begin = ind
			break
	return fname[:-ext_begin] + '.' + ext


def get_ext(fname):
	'''Returns (fname (not including extension), extension).'''
	for ii in range(len(fname)-1,0,-1):
		if fname[ii]=='.':
			return fname[:ii],fname[ii:]
	return fname,''


def increment_name(fname,check_dups = True,start_num = 0):
	'''If fname is not the name of an extant file, returns fname. Else:
Create a new file name with _{number} appended to the end of fname,
where "number" is either start_num (if check_dups is False or
no file already exists with that extension) or the lowest integer n greater
than start_num such that no file namedfname+"_"+str(n)+(fname's extension)
already exists with that extension.'''
	fname = os.path.abspath(fname)
	stem,ext = get_ext(fname)
	if not check_dups:
		return stem+'_'+str(start_num)+ext
	else:
		if not (os.path.exists(fname) or os.path.isfile(fname)):
			return fname
		ii = start_num
		while True:
			new_ext = stem+'_'+str(ii)+ext
			if not os.path.exists(new_ext):
				return new_ext
			ii += 1

			
from encodings_text_files import encodings
#includes something like 100 different encodings, starting with the most common
def get_text_best_encoding(fname, print_on_exception = False):
	for enc_num,encoding in enumerate(encodings):
		try:
			with open(fname,'r', encoding = encoding) as f:
				#print(encoding,end=', ')
				return f.read() #we found a good encoding, stop trying new ones.
		except:
			pass #keep trying other encodings
	if enc_num >= len(encodings)-1:
		if not print_on_exception:
			raise UnicodeDecodeError("Could not find the encoding for this file.")
		print("Could not find the encoding for this file.")

textTypeFiles = "\.(txt|py|ipynb|json|js|htm[l]?|css|[ct]sv|R|Rmd|sql|fwf|c|cpp|bat)$"

grepParser = re.compile(("(?P<options>(?:-[a-z\d]+\s+)*)"
						  "'(?P<regex>.+)' "
						  "(?P<File_or_containing_directory>/.+)"))


def grep(Input):
	"""The grep filter searches a .txt file for a particular pattern of characters,
and displays all lines that contain that pattern. The pattern that is searched
in the file is referred to as the regular expression
(grep stands for globally search for regular expression and print out).
grep has an "options" attribute so you can see the options you can use.

Format for Input:
[options] 'pattern' /[filename or containing directory]

Alternative format for input:
[options 1] '[pattern 1]' /[containing dir] -}} [options 2] '[pattern 2]'
	( -}} ... -}} [options n] '[pattern n]')?
	If the command is in this alternative format, finds the set of files in
	[containing dir] that satisfy the first query, then uses each query
	between the first and the last to refine the set of files, and returns
	the results of the final query.
	See subGrep.

By default, returns a dict mapping filenames to a list of lines in that file
	where the regex is matched. Some options change the return type.

IMPORTANT: You NEED to have exactly one space between the options block and
the pattern block, the pattern block MUST be enclosed by '', there MUST
be exactly one space between the pattern block and the filename block, and
the filename block must be preceded by /.

Options Description
-f : Searches only the filenames of text-type files for matches to the regex. 
	(returns list)
-a : Special case of -f. Matches regex in filenames of all files, not just 
	text-type files.
-c : This prints only a count of the lines that match a pattern 
	(returns dict)
-h : Display the matched lines, but do not display the filenames. 
	(returns list)
-i : case-insensitive match
	(does not affect return type)
-l : Displays list of a filenames only. 
	(returns list)
-n : Display the matched lines and their line numbers. 
	(returns dict mapping to tuples)
-v : Matches all the lines that DO NOT match the pattern
	(does not affect return type)
-o : Match whole word or filename. For filenames, matches only the part
	of the filename that is not in the parent directory name (so any subdir
	name plus the file name in the -r case or just the filename otherwise).
-d : Searches only directory names for matches to the regex.
	(returns list)
-r : Recursively searches through the entire directory tree beneath a given
	directory (all subdirectories within that directory as well as the 
	directory itself)
	(does not affect return type)
	"""
	if ' -}} ' in Input:
		greps = [x.strip() for x in Input.split(' -}} ')]
		return subGrep(greps)
		
	
	parsedInput = re.findall(grepParser, Input.strip())[0]
	options = list(map(lambda x: x.lower().strip(),
					filter(lambda x: len(x)>0,
						   re.split("(?:\s+|^)-",parsedInput[0])
						   ))) 
	#split the options substring into letters, convert to lower-case
	
	regex = parsedInput[1]
	dirName = os.path.abspath(str.join("\\", parsedInput[2].split('/')[1:]))
	
	#print(options,regex,dirName)

	c = ('c' in options)
	h = ('h' in options)
	i = ('i' in options)
	l = ('l' in options)
	n = ('n' in options)
	v = ('v' in options)
	d = ('d' in options)
	o = ('o' in options)
	r = ('r' in options)
	f = ('f' in options)
	a = ('a' in options)

	goodFiles = {}
	goodFilesLineNums = {}
	goodDirs = []
	
	if i:
		if o:
			goodness_condition = lambda line: any((re.fullmatch(regex,x,re.I) is not None) \
													for x in line.split())
			f_goodness_condition = lambda fname: re.fullmatch(regex,fname,re.I) is not None
		else:
			goodness_condition = lambda line: re.search(regex,line,re.I) is not None
			f_goodness_condition = lambda fname: re.search(regex,fname,re.I) is not None
	else:
		if o:
			goodness_condition = lambda line: any((re.fullmatch(regex,x) is not None) \
													for x in line.split())
			f_goodness_condition = lambda fname: re.fullmatch(regex,fname) is not None
		else:
			goodness_condition = lambda line: re.search(regex,line) is not None
			f_goodness_condition = lambda fname: re.search(regex,fname) is not None
	
	dirIsFile = os.path.isfile(dirName)
	if not dirIsFile:
		try:
			if r:
				filesToSearch=[]
				for root, dirs, files in os.walk(dirName):
					if d:
						for Dir in dirs:
							Dir = os.path.join(root,Dir)
							if f_goodness_condition(Dir) ^ v: #hooray for XOR!!
								goodDirs.append(Dir)
						continue
					for fname in files:
						filesToSearch.append(os.path.join(root, fname))
			else:
				filesToSearch = os.listdir(dirName)
				if d:
					for thing in filesToSearch:
						Dir = os.path.join(dirName,thing)
						if os.path.isdir(Dir) and f_goodness_condition(Dir) ^ v:
							goodDirs.append(Dir)
		except:
			# if re.search(textTypeFiles, fname):
				# dirIsFile = True
			filesToSearch = []
		
		if d:
			if f_goodness_condition(dirName) ^ v:
				goodDirs.append(dirName) #need to consider the starting dir too
			filesToSearch = [] #consider only directories with d option
		
		for fname in filesToSearch:
			file = os.path.join(dirName,fname)
			if f and a:
				if f_goodness_condition(fname) ^ v:
					goodFiles.setdefault(file,0)
			elif (re.search(textTypeFiles, fname)):
				if f:
					if f_goodness_condition(fname) ^ v:
						goodFiles.setdefault(file,0)
					continue
				lines = get_text_best_encoding(file,print_on_exception=True).split('\n')
				for ind in range(len(lines)):
					line=lines[ind]
					if goodness_condition(line) ^ v:
						goodFiles.setdefault(file, [])
						goodFiles[file].append(line)
						goodFilesLineNums.setdefault(file, [])
						goodFilesLineNums[file].append((ind, line))

	if dirIsFile:
		file=dirName
		if f:
			if f_goodness_condition(file) ^ v:
				goodFiles.setdefault(file,0)
		else:
			lines = get_text_best_encoding(file,print_on_exception=True).split('\n')
			for ind in range(len(lines)):
				line = lines[ind]
				if goodness_condition(line) ^ v:
					goodFiles.setdefault(dirName, [])
					goodFiles[dirName].append(line)
					goodFilesLineNums.setdefault(dirName, [])
					goodFilesLineNums[dirName].append((ind, line))
	
	
	if d:
		return goodDirs
	if f:
		return list(goodFiles.keys())
	
	if c:
		fileLineCounts={}
		for key in goodFiles:
			fileLineCounts[key] = len(goodFiles[key])
		return fileLineCounts
	if h:
		linelist=[]
		linelistWithNums=[]
		for key in goodFiles:
			for ind in range(len(goodFiles[key])):
				line = goodFiles[key][ind]
				linelist.append(line)
				linelistWithNums.append((ind, line))
		if n: 
			return linelistWithNums
		return linelist
	if n:
		return goodFilesLineNums
	if l:
		return list(goodFiles.keys())
	return goodFiles

grep.options = ('-a(ll file types)',
 '-c(ount occurrences of pattern)',
 '-d(irectories only)',
 '-f(ilenames and directories only)',
 '-h (display lines, not files)',
 '-i (case insensitive)',
 '-l (list filenames)',
 '-n (line Numbers only)',
 '-o (match only entire words)',
 '-r(ecursive search)',
 '-v (display only things that DON\'T match)')

def subGrep(greps):
	'''Iterates through the grep queries in greps. Generates a set of files
with the first grep query.
Uses each grep query between the first and the last to iteratively refine 
this result set, and returns the union of results from the last query made
on the result set generated by the penultimate query.
	'''
	# print(greps)
	# print()
	resultset = grep(greps[0])
	options = grepParser.findall(greps[0])[0]
	# print(resultset)
	# print()
	for Grep in greps[1:-1]:
		Grep = Grep.strip()
		# print(Grep)
		new_results = []
		for fname in resultset:
			new_results.extend(grep(Grep+' /'+fname))
		resultset = new_results
		# print(resultset)
		# print()
	
	if re.search('-[dhfl]',greps[-1]):
		output = []
		for f in resultset:
			output.extend(grep(greps[-1]+' /'+f))
	else:
		output = {}
		for f in resultset:
			output.update(grep(greps[-1]+' /'+f))
	return output


def sed(grep_or_fname,regex,repl,ask_permission = True,name_mangle = '_sed',flags=0):
	"""Search for regex in files, replace them, writing to new files if desired.
grep_or_fname: a filename, a list of filenames, or a grep query for
	filenames.
regex: string, a regular expression or string to be replaced.
repl: string, a pattern for replacing the string in the file(s).
ask_permission: bool. If True, shows what will be replaced before each
	replacement, and allows you to quit at any point if you want.
name_mangle: string. If '', files will be overwritten by this function.
	THIS IS OBVIOUSLY DANGEROUS! Thus, the default is to write a new file
	with '_sed' appended to the filename.

Solution: http://thinkpython2.com/code/sed.py.
meat=re.compile('meat', flags=re.I)
Test for non-recursive form: gsfd.sed('ludd', 'eehive', './/delicious//bluddText inc15.txt')
Test for recursive form: gsfd.sed(meat, 'tofu', './/delicious', recursive=True)
Test for non-recursive form with name choice: gsfd.sed('ludd', 'eehive', 'bluddNew.txt', './/delicious//bluddText inc15.txt')
Test for error handling in recursive form: gsfd.sed('dfd', '23rer', '33254223432', recursive=True)
Test for error handling in non-recursive form: gsfd.sed('dfd', '23rer', '33254223432')
zargothrax=gsfd.grep("-i -r 'argothrax' /C:/Users/molso/Documents/html stuff")
	"""
	try:
		is_grep_query = not os.path.isfile(grep_or_fname)
	except: #it's an iterable of file names, not a string, which causes error
		is_grep_query = False
	findregex = re.compile(regex,flags)
	if is_grep_query:
		files = grep(grep_or_fname)
	else:
		if is_iterable(grep_or_fname):
			files = list(grep_or_fname)
		else:
			files = [grep_or_fname]
	if len(files)==0:
		print("No files found.")
	for file in files:
		try:
			text = get_text_best_encoding(file)
		except:
			print(f"File {file} not found, or its encoding could not be determined.")
			continue
		newtext = ''
		last_index = 0
		if ask_permission:
			print(f"\nNow in file {file}.")
			has_replacements = False
			for to_replace in findregex.finditer(text):
				has_replacements = True
				start,end= to_replace.span()
				newtext += text[last_index:start]
				old = text[start:end]
				new_ = findregex.sub(repl,old)
				last_index = end
				decision = input((f"\nAre you sure you want to replace \"{old}\""
						   f" with \"{new_}\"?"
						   "\nIf yes, press 1. If no, press something else."
						   "\nIf you don't want to be asked permission again, press 99.\t"))
				if decision not in ['1','99']:
					next_decision = input(("\nPrematurely terminating replacements."
						   " Press 1 to continue to other files, "
						   "or something else to exit function.\t"))
					if next_decision == '1':
						newtext += old
						break
					else:
						return
				newtext += new_
				if decision == '99':
					print("\nPermission will no longer be requested.")
					newtext += findregex.sub(repl,text[end:])
					last_index = len(text)
					ask_permission = False
					break
			newtext += text[last_index:]
		else: #not requesting permission
			has_replacements = True
			newtext += findregex.sub(repl,text)
		if has_replacements: #only overwrite file if anything has been changed
			fname,ext = get_ext(file)
			if name_mangle != '':
				newfile = increment_name(fname + name_mangle + ext)
			else:
				newfile = file
			#this will overwrite old file if name_mangle is ''
			with open(newfile,'w') as f:
				f.write(newtext)
	return
