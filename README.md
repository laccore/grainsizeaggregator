# grainsizeaggregator
Python script that aggregates grain size CSVs into a single Excel file.
Each grain size CSV has three columns. The second column of each file
contains the data of interest. Each column is extracted as a row, and
combined with the first column of any file (it should be identical in
all files), which is used as a header row.
