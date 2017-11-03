'''
Created on Jun 22, 2017

@author: bgrivna

Qt GUI main for gsaggregator
'''

import os
import sys

from PyQt5 import QtWidgets

import gsagg

class AggregatorWindow(QtWidgets.QWidget):
    def __init__(self, app):
        self.app = app
        self.lastFileDialogPath = os.path.expanduser("~")
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle("CSDCO/LacCore Grain Size Aggregator {}".format(gsagg.Version))
        
        self.gsDirText = LabeledLineText(self, "Grain Size Directory")
        self.chooseGSDirButton = QtWidgets.QPushButton("...", self)
        self.chooseGSDirButton.clicked.connect(self.chooseGSDir)
        self.outputPathText = LabeledLineText(self, "Output File")
        self.chooseOutputFileButton = QtWidgets.QPushButton("...", self)
        self.chooseOutputFileButton.clicked.connect(self.chooseOutputFile)
        
        vlayout = QtWidgets.QVBoxLayout(self)
        dirlayout = self.makeFileLayout(self.gsDirText, self.chooseGSDirButton, "Directory containing grain size files - all *.csv files will be processed")
        vlayout.addLayout(dirlayout)
        outputlayout = self.makeFileLayout(self.outputPathText, self.chooseOutputFileButton, "File to which aggregated grain size data will be written")
        vlayout.addLayout(outputlayout)
        
        vlayout.addWidget(QtWidgets.QLabel("Log!", self))
        self.logArea = QtWidgets.QTextEdit(self)
        self.logArea.setReadOnly(True)
        self.logArea.setToolTip("Big, Heavy, Wood!")
        vlayout.addWidget(self.logArea)
        
        self.aggButton = QtWidgets.QPushButton("Let's Aggregate!")
        self.aggButton.clicked.connect(self.aggregate)
        vlayout.addWidget(self.aggButton, stretch=1)

    def aggregate(self):
        gsDir = self.gsDirText.text()
        if not os.path.exists(gsDir):
            self._warnbox("Badness", "Grain Size directory {} does not exist".format(gsDir))
            return
        outFile = self.outputPathText.text()
        if not os.path.exists(os.path.dirname(outFile)):
            self._warnbox("Badness", "Destination directory {} does not exist".format(os.path.dirname(outFile)))
            return

        self.aggButton.setEnabled(False)
        self.logArea.clear()
        try:
            gsFiles = self.gatherGSFiles(gsDir)
            gsa = gsagg.GrainSizeAggregator(self.report)
            gsa.aggregate(gsFiles, outFile)
        except Exception as err:
            self.report("\nSUPER FATAL ERROR: " + str(err))
        self.aggButton.setEnabled(True)
        
    def gatherGSFiles(self, gsDir):
        return [os.path.join(gsDir, f) for f in os.listdir(gsDir) if f.endswith('.csv')]
        
    def report(self, text):
        text += "\n"
        self.logArea.insertPlainText(text)
        self.app.processEvents() # force GUI update
        
    def _warnbox(self, title, message):
        QtWidgets.QMessageBox.warning(self, title, message)
        
    def chooseGSDir(self):
        dlg = QtWidgets.QFileDialog(self, "Choose Grain Size directory", self.lastFileDialogPath)
        selectedDir = dlg.getExistingDirectory(self)
        if selectedDir != "":
            self.report("Selected Grain Size directory {}".format(selectedDir))
            self.gsDirText.setText(selectedDir)
        
    def chooseOutputFile(self):
        dlg = QtWidgets.QFileDialog(self, "Choose output file", self.lastFileDialogPath)
        selectedFile, dummyFilter = dlg.getSaveFileName(self)
        if selectedFile != "":
            if not selectedFile.lower().endswith('.csv'):
                selectedFile += '.csv'
            self.report("Selected output file {}".format(selectedFile))
            self.outputPathText.setText(selectedFile)
    
    def makeDescLabel(self, desc):
        label = QtWidgets.QLabel(desc)
        label.setStyleSheet("QLabel {font-size: 11pt;}")
        return label
    
    # return layout with editText (includes label) and chooserButton on one line,
    # descText on the next with minimal vertical space between the two
    def makeFileLayout(self, editText, chooserButton, descText):
        layout = QtWidgets.QVBoxLayout()
        hlayout = QtWidgets.QHBoxLayout()
        hlayout.addWidget(editText)
        hlayout.addSpacing(10)
        hlayout.addWidget(chooserButton)
        layout.addLayout(hlayout)
        layout.setSpacing(0)
        layout.addWidget(self.makeDescLabel(descText))
        return layout

class LabeledLineText(QtWidgets.QWidget):
    def __init__(self, parent, label):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.label = QtWidgets.QLabel(label, parent)
        self.edit = QtWidgets.QLineEdit(parent)
        layout.addWidget(self.label)
        layout.addSpacing(10)
        layout.addWidget(self.edit)
        
    def text(self):
        return self.edit.text()
    
    def setText(self, newText):
        self.edit.setText(newText)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AggregatorWindow(app)
    window.show()
    sys.exit(app.exec_())