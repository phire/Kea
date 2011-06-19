from PySide.QtCore import *
from PySide.QtGui import *

class Text(object):
	def __init__(self, text, color=(0, 0, 0), mouseOver=None):
		self.text = text
		self.color = color
		self.mouseOver = None
		
	def __str__(self):
		return self.text

class Tab(object):
	def __init__(self, stop):
		self.stop = stop

gray = (150, 150, 150)
blue = (0, 60, 200)
green = (0, 200, 60)
orange = (255, 176, 31)

class AsmArea(QWidget):
	def __init__(self, parent=None):
		super(AsmArea, self).__init__(parent)

		self.setBackgroundRole(QPalette.Base)
		self.setAutoFillBackground(True)

		self.text = [[Text("ROM0:0150", gray), Tab(100), Text("cp ", blue), Text("a", orange), Text(", ", blue), Text("0x11", green)],[Text("ROM0:0152", gray), Tab(100), Text("jr ", blue), Text("z", orange), Text(", ", blue), Text("0x157", green)]]
		self.setMouseTracking(True)

		self.font = QFont("Courier", 10)
		self.fm = QFontMetrics(self.font)
		self.h = self.fm.height() 
		self.setFont(self.font)
		self.highlightLine = 0

	def mouseMoveEvent(self, event):
		self.highlightLine = event.pos().y() / self.h
		self.repaint() #todo: paint only when highligh line changes

	def paintEvent(self, event):
		painter = QPainter(self)

		painter.fillRect(0, self.h * self.highlightLine, self.width(), self.h, self.palette().alternateBase())

		for i,line in enumerate(self.text, 1):
			x = 5
			for word in line:
				if type(word) is Tab:
					x = max(word.stop, x)
					continue
				painter.setPen(QColor(*word.color))
				painter.drawText(x, i * self.h - self.fm.descent(), word.text)
				x += self.fm.width(word.text)

