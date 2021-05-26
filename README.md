# Python-utility-functions
This is a grab-bag of stuff I created "just because".

<b style = 'font-size:115%'>In chronological order (periodically reordered according to my perception of the function's importance or actual utility):</b>
<li>
  <b>1.</b> grep: Not just for searching for text in files! Can also:<ul>
    <b>-</b> search for filenames (which can include non-text files) and directory names matching regexes<br>
    <b>-</b> use pipes to successively refine file searches<br>
    <b>-</b> Write results to JSON files<br>
    <b>-</b> Order results by (and view) last modification time or file size<br>
    <b>-</b> Limit number of files returned (useful when ordering by mod time or size)
    <b>-</b> Automatically open all files found by the search (Windows only)
  </ul>
  <b>2.</b> json_funcs: Two functions that do depth-first search in JSON.<ul>
    One pretty-prints only the keys of dicts (not the values), which can prove handy when JSON has a lot of long values (e.g., tweets).<br>
    Another extracts JSON that lies along a partially specified path. This is my JSON-extraction function. There are many like it, but this one is mine!
  </ul>
  <b>3.</b> numpy_to_latex and numpy_array_from_string:<ul>
    numpy_to_latex converts a numpy array into a syntactically correct $\LaTeX$ matrix.<br>
    numpy_array_from_string reads any string representation of a numpy array back to the original array, with or without commas.
  </ul>
 </li>
That's all so far!
