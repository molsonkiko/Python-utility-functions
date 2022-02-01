# Python-utility-functions
This is a grab-bag of stuff I created "just because".

grep and json_funcs are superseded by "gorpy", my newer project. Don't bother with them.

<b style = 'font-size:115%'>In order of perceived importance:</b>
<li>
  <b>1.</b> split_into_subframes:<ul>
    When you're using pandas.read_excel to parse an Excel workbook or similar, you will often find a single table that should properly be broken up into multiple tables.<br>
    split_into_subframes.split_into_subframes breaks down pandas DataFrames into sub-tables so that none of them have any empty rows or columns, which can often help with sheets that contain multiple tables.
  </ul>
  <b>2.</b> parse_num_range:<ul>
    Utilities for converting strings representing ranges of numbers (e.g., ["1-10", "$10 to $1,000"]) into actual numeric ranges.<br>
    For example, ["Under 10 years", "10 years old", "11-20", "21-40", "over 40"] could be correctly parsed as the ranges [(0, 10), (10, 11), (11, 20), (21, 40), (40, inf)]
  </ul>
  <b>3.</b> map_bins:<ul>
    When you're working with census data or similar, you often come across data that is binned and you have no access to the underlying numbers.<br>
    This allows you to increase the data's bin size, so that you can easily go from, say, 10-year age increments to 20-year age increments.
  </ul>
  <b>4.</b> multiple_instances_same_keys:<ul>
    Given a JSON or YAML document that contains dicts with multiple instances of the same key, creates a new Python object where each multiple-key is mapped to a list of the values it was assigned to.
  </ul>
  <b>5.</b> numpy_to_latex and numpy_array_from_string:<ul>
    numpy_to_latex converts a numpy array into a syntactically correct $\LaTeX$ matrix.<br>
    numpy_array_from_string reads any string representation of a numpy array back to the original array, with or without commas.
  </ul>
  <b>6.</b> grep (requires gsfd, encodings_text_files). <b>Don't bother, use gorpy instead.</b> Can search text files and also the following: <ul>
    <b>-</b> be called from the command line<br>
    <b>-</b> search for filenames (which can include non-text files) and directory names matching regexes<br>
    <b>-</b> use pipes to successively refine file searches<br>
    <b>-</b> Write results to JSON files<br>
    <b>-</b> Order results by (and view) last modification time or file size<br>
    <b>-</b> Limit number of files returned (useful when ordering by mod time or size)<br>
    <b>-</b> Automatically open all files found by the search (Windows only)
  </ul>
  <b>7.</b> json_funcs: Two functions that do depth-first search in JSON. <b>Use gorpy's gorp.jsonpath instead.</b><ul>
    One pretty-prints only the keys of dicts (not the values), which can prove handy when JSON has a lot of long values (e.g., tweets).<br>
    Another extracts JSON that lies along a partially specified path. This is my JSON-extraction function. There are many like it, but this one is mine!
  </ul>
 </li>
That's all so far!
