'''
Created on Nov 2, 2017
@author: bgrivna

Script to aggregate grain size CSVs into a single CSV. Each grain size
CSV has three columns. The second column of each file contains the data
of interest. Each column is extracted as a row, and combined with 
the first column of any file (it should be identical in all files),
which is used as a header row.
'''

from os import listdir

import pandas

Version = '0.0.3'

class GrainSizeAggregator:
    def __init__(self, reporter):
        self.reporter = reporter

    # files - list of paths to CSV files to be aggregated
    # outputPath - destination path of aggregated CSV
    def aggregate(self, files, outputPath):
        if len(files) == 0:
            return
        
        gsRows = []
        for index, f in enumerate(files):
            df = self.openGrainSizeCSV(f)
            if index == 0:
                # pull first column from first file for headers in aggregated file
                headers = self.getColAsRow(df, 'A')
            row = self.getColAsRow(df, 'B')
            
            if len(row) != len(headers):
                raise Exception("Grain size file {} contains {} rows, differs from expected {}".format(f, len(row), len(headers)))

            gsRows.append(row)
        
        # combine header with values and export an Excel File
        aggRows = pandas.DataFrame(gsRows)
        aggRows.columns = headers
        #aggRows.to_csv(outputPath, index=False)
        aggRows.to_excel(outputPath, sheet_name="Aggregated Grain Sizes", index=False)
        self.log("Writing grain size data from {} files to {}...".format(len(gsRows), outputPath))
        self.log("Process completed successfully!")

    def openGrainSizeCSV(self, csvpath):
        self.log("opening {}".format(csvpath))
        
        # all files are coming from a Windows machine, interpret as CP-1252 to avoid
        # issues encoding as UTF-8 when writing aggregated results to an Excel file.
        return pandas.read_csv(csvpath, names=['A', 'B', 'C'], encoding='cp1252')
    
    def getColAsRow(self, dataframe, col):
        return pandas.Series(dataframe[col].values.reshape(1,-1)[0])
    
    def log(self, text):
        self.reporter(text)

def report(text):
    print(text)

if __name__ == '__main__':
    files = [] # RGB files to aggregate
    gsa = GrainSizeAggregator(report)
    gsa.aggregate(files, "aggOutput.csv")