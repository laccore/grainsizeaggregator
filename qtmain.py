'''
Created on Jun 22, 2017

@author: bgrivna

Qt GUI main for gsaggregator
'''

import os
import sys
import platform
import traceback

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
        dir_text = "Directory containing grain size files. All *.csv and *.txt files will be processed."
        dirlayout = self.makeFileLayout(self.gsDirText, self.chooseGSDirButton, dir_text)
        vlayout.addLayout(dirlayout)
        self.subdirsBox = QtWidgets.QCheckBox("Include subdirectories", self)
        self.subdirsBox.setStyleSheet(getPlatformStyleSheet())
        vlayout.addWidget(self.subdirsBox)
        vlayout.addSpacing(20)
        output_text = "Excel file to which aggregated grain size data will be written."
        outputlayout = self.makeFileLayout(self.outputPathText, self.chooseOutputFileButton, output_text)
        vlayout.addLayout(outputlayout)
        vlayout.addSpacing(15)
        
        vlayout.addWidget(makeItemLabel("Log!"))
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
            self._warnbox("Badness", "Output directory {} does not exist".format(os.path.dirname(outFile)))
            return

        self.aggButton.setEnabled(False)
        self.logArea.clear()
        try:
            gsFiles = self.gatherGSFiles(gsDir, include_subdirs=self.subdirsBox.isChecked())
            gsa = gsagg.GrainSizeAggregator(self.report)
            gsa.aggregate(gsFiles, outFile)
        except Exception as err:
            errstr = "SUPER FATAL ERROR: " + str(err)
            self.report(errstr)
            self.report(traceback.format_exc())
            self._errbox("Fatal Error", str(err))
        self.aggButton.setEnabled(True)

    def valid_extension(self, filename):
        return filename.endswith('csv') or filename.endswith('txt')

    def gatherGSFiles(self, gsDir, include_subdirs):
        if include_subdirs:
            gs_files = []
            for dirpath, _, filenames in os.walk(gsDir):
                gs_files += [os.path.join(dirpath, f) for f in filenames if self.valid_extension(f)]
            return gs_files
        else:
            return [os.path.join(gsDir, f) for f in os.listdir(gsDir) if self.valid_extension(f)]
        
    def report(self, text):
        text += "\n"
        self.logArea.insertPlainText(text)
        self.app.processEvents() # force GUI update
        
    def _warnbox(self, title, message):
        QtWidgets.QMessageBox.warning(self, title, message)
        
    def _errbox(self, title, message):
        QtWidgets.QMessageBox.critical(self, title, message)        
        
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
            if not selectedFile.lower().endswith('.xlsx'):
                selectedFile += '.xlsx'
            self.report("Selected output file {}".format(selectedFile))
            self.outputPathText.setText(selectedFile)
    
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
        layout.addWidget(makeDescLabel(descText))
        return layout

def getPlatformStyleSheet():
    return "QCheckBox {font-size: 9pt;}" if platform.system() == "Windows" else "QCheckBox {font-size: 11pt;}" 

def makeDescLabel(text):
    label = QtWidgets.QLabel(text)
    ss = "QLabel {font-size: 9pt;}" if platform.system() == "Windows" else "QLabel {font-size: 11pt;}" 
    label.setStyleSheet(ss)
    return label

def makeItemLabel(text):
    label = QtWidgets.QLabel(text)
    if platform.system() == "Windows":
        label.setStyleSheet("QLabel {font-size: 11pt;}")
    return label

class LabeledLineText(QtWidgets.QWidget):
    def __init__(self, parent, label):
        QtWidgets.QWidget.__init__(self, parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.label = makeItemLabel(label)
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