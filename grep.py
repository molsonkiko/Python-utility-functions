from gsfd import grep,increment_name
import re
import time
import os
import sys
from dateutil import parser
from commanum import format_bytes

def fname_checker(fname,ext):
	ext_begin = -len(fname)
	for ind in range(1,len(fname)+1):
			ext_begin = ind
		if fname[-ind]=='.':
			break
	return fname[:-ext_begin] + '.' + ext

def last_mod_time(fname,as_datetime=False):
	'''Get the last time the file named fname was modified.
Default return value is a formatted datetime string. If as_datetime, then 
return a datetime.datetime object representing that time.'''
	mod_time_seconds = os.path.getmtime(fname)
	formatted_time_string = time.ctime(mod_time_seconds)
	if as_datetime:
		return parser.parse(formatted_time_string)
	else:
		return formatted_time_string


def filesize(f):
	return os.path.getsize(f)

queryParser = "\s*(?P<options>(?:-[a-z\d]+\s+)*)(?P<text>'.+?')(?:\s+(?P<fname>/[^}\t]+)(?: -}} |\s*$))?"

w_query_splitter = " -}} \s*-w\s+'(.+)'"


def has_option(Grep_,option):
	options,regexes,fnames = list(zip(*re.findall(queryParser,Grep_)))
	return any((option in x) for x in options)

helpstring = '''Welcome to the grep prompt.
You can exit at any time by entering 'e','q','quit', or 'exit'.
Enter "options" for a list of grep's optional arguments.
You can display the working directory with 'd' or 'dir', change the working
directory with 'cd <new directory name>', and display the contents of the
working directory with 'ls'.
You can write the results of a query to a JSON file by terminating the query
with " -}} -w '<name of file to write to>'.
Finally, you can supply a numeric argument to limit the size of the resultset.
'''

grep.options = ('-a(ll file types)',
 '-c(ount occurrences of pattern)',
 '-d(irectories only)',
 '-f(ilenames and directories only)',
 '-h (display lines, not files)',
 '-i (case insensitive)',
 '-l (list filenames)',
 '-m (get last Modification time)',
 '-n (line Numbers only)',
 '-o (match only entire words)',
 '-p (oPen all files in the final resultset with their default apps)',
 '-s(izes of files found)',
 '-t (number of files found (and total size if -s arg used)',
 '-r(ecursive search)',
 '-v (display only things that DON\'T match)',
 '-w (write results of query to a JSON file)')
 
def process_grep_query(query, mode = 'print', has_warned_fname = False):
	try: #make the query
		parsed_query = [re.findall(queryParser, x)[0] for x in query.split('-}}')]
		options, regexes,fnames = list(zip(*parsed_query))
		if fnames[0] == '':
			if not has_warned_fname:
				print("WARNING: You should always include /<directory path> after the first regex.")
				print("When none is listed, the current directory (/.) will automatically be used.")
				print()
			has_warned_fname = True
			query = ' '.join(parsed_query[0][:2]+('/.',))
			for q in parsed_query[1:]:
				query += ' -}} '+' '.join(q)
		w_option, p_option = False,False
		if 'w' in options[-1]:
			query,write_to_name,_ = re.split(w_query_splitter,query)
			w_option = True
		#print(repr(query))
			
	except (IndexError,ValueError):
		print("That's not a recognized command. Try again.")
		return
	
	try:
		resultset = grep(query)
	except (IndexError,re.error):
		print("Malformed query. Try again.")
		return
	m_option = any(('m' in x) for x in options)
	if m_option:
		modtime_d = [(f,last_mod_time(f,True)) for f in resultset]
		modtime_d.sort(key=lambda x: x[1],reverse=True)
		modtime_d = [(x,str(y)) for x,y in modtime_d]
		resultset = modtime_d
		del modtime_d
	
	t_option = any(('t' in x) for x in options) # used -t option, get count of files and sum of sizes
	if any(('s' in x) for x in options): # find file sizes
		if not m_option:
			sizes = [(f, filesize(f)) for f in resultset]
			if t_option:
				sizes = [len(resultset), format_bytes(sum(x[1] for x in sizes))]
			else:
				sizes.sort(key = lambda x: x[1], reverse = True)				
				sizes = [(x, format_bytes(y)) for x,y in sizes]
		else:
			sizes = [f + (filesize(f[0]),) for f in resultset]
			if t_option: 
				sizes = [len(resultset), format_bytes(sum(x[2] for x in sizes))]
			else:
				sizes.sort(key = lambda x: x[2], reverse = True)
				sizes = [(x, y, format_bytes(z)) for x,y,z in sizes]
		resultset = sizes
		del sizes
	elif t_option:
		resultset = len(resultset)
		
	for optset in options:
		num = re.findall('\d+', optset)
		if len(num) > 0:
			resultset = resultset[:int(num[0])] 
			# truncate resultset to n responses, where n is numeric arg
	
	if any(('p' in x) for x in options): #used -p option, open files
		p_option = True
		if mode == 'print':
			print(resultset)
		opening_decision = 'y'
		if len(resultset) > 5:
			opening_decision = input(f"This resultset includes {len(resultset)} files. Are you sure you want to open all of them (y/n)?\n")
		if opening_decision =='y':
			## open each file with default application
			for filename in resultset:
				if isinstance(filename,tuple): # '-m' option or '-s' option used
					filename = filename[0]
				os.startfile(filename) #only works on Windows unfortunately
				#import subprocess
				#subprocess.run([filename],shell=True,check=True) #alternative that probably generalizes better
				#could also probably use subprocess.Popen(executable,filename) to specify an application
	
	if w_option: #used -w option, write results to files
		import json
		write_to_name = increment_name(fname_checker(write_to_name,'json'))
		with open(write_to_name,'w') as f:
			json.dump(resultset,f)
		del write_to_name
	
	if mode == 'print':
		if not (p_option | w_option): # just print results
			print(resultset)
		return has_warned_fname
	return resultset


def main():
	has_warned_fname = False
	args = sys.argv
	if len(args) > 1: #first arg is always path to the module's file
		query = ' '.join(args[1:])
		has_warned_fname = process_grep_query(query, 'print', has_warned_fname)
		return
	print(helpstring)
	while True:
		#break
		#query = input("Enter a query, 'q' or 'e' to exit, 'o' for options, 'h' for help.\ngrep> ").strip()
		query = input("grep> ")
		if query in ['h','help']:
			print(helpstring)
			continue
		elif query in ['o', 'options']:
			print(grep.options)
			continue
		elif query in ['e','q','exit','quit']:
			print("\nGoodbye!")
			break
		elif query in ['dir','d']:
			print(os.getcwd())
			continue
		elif query[:2].lower() =='cd':
			newdir = re.sub("^\s*cd\s+",'',query)
			newdir = re.sub('\'|"','',newdir)
			try:
				os.chdir(newdir)
			except FileNotFoundError:
				print(f"The directory {newdir} was not found.")
			continue
		elif query=='ls':
			print(os.listdir('.'))
			continue
		else: #parse the query as a grep query
			has_warned_fname = process_grep_query(query, 'print', has_warned_fname)
		print()
		del query
	return None

	
if __name__ == '__main__':
	main()


example_greps = ["-w 'foo.bar.csv'",
					"-p -i 'jubar'",
					"-p '.'"]


fullGreps = ["-i -f -r 'zebra' /delicious -}} -30 'meat' -}} -w 'foo.bar.csv'",
				"-i -f -r 'zebra' /delicious -}} -p -l 'meat'",
				"-i -f -r 'zebra' /delicious -}} -m 'meat'",
				"-p -i -f -r '[^w].+zebra' /delicious",
				" 'zebra' /delicious",
				"'zebra' /delicious\t"]
