#!/usr/bin/python

import sys
from PySide.QtCore import *
from PySide.QtGui import *
from asmWidget import AsmArea

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()

		self.createMenus()
		self.asmArea = AsmArea()
		self.setCentralWidget(self.asmArea)

		self.setWindowTitle("kea")
		self.resize(800,600)

	def createMenus(self):
		self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
			triggered=self.close)

		fileMenu = QMenu("&File", self)
		fileMenu.addAction(self.exitAct)
		
		self.menuBar().addMenu(fileMenu)

app = QApplication(sys.argv)

main = MainWindow()
main.show()

app.exec_()
sys.exit()
