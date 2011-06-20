from PySide.QtCore import *
from PySide.QtGui import *

class Text(object):
	def __init__(self, text, color=(0, 0, 0)):
		self.text = text
		self.color = color
		
	def __str__(self):
		return self.text

	def mouseIn(self, widget):
		self.oldColor = self.color
		self.color = (255, 0, 0)
		widget.repaint()
	
	def mouseOut(self, widget):
		self.color = self.oldColor
		widget.repaint()

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

		text = [[Text("ROM0:0150", gray), Tab(100), Text("cp ", blue), Text("a", orange), Text(", ", blue), Text("0x11", green)],[Text("ROM0:0152", gray), Tab(100), Text("jr ", blue), Text("z", orange), Text(", ", blue), Text("0x157", green)]]
		self.setMouseTracking(True)

		self.font = QFont("Courier", 10)
		self.fm = QFontMetrics(self.font)
		self.h = self.fm.height() 
		self.setFont(self.font)
		self.highlightLine = 0
		self.setContent(text)
		self.hover = None

	def setContent(self, content):
		self.text = content
		for line in self.text:
			x = 5
			for word in line:
				word.left = x
				if type(word) is Tab:
					x = max(word.stop, x)
				else:
					x += self.fm.width(str(word))
				word.right = x

	def mouseMoveEvent(self, event):
		if not self.highlightLine == event.pos().y() / self.h:
			self.highlightLine = event.pos().y() / self.h
			self.repaint()
		x = event.pos().x()
		try:
			hover = filter(lambda w: w.left < x and w.right > x, self.text[self.highlightLine])[0]
		except IndexError:
			hover = None
		if hover is not self.hover:
			try:
				hover.mouseIn(self)
			except AttributeError:
				pass
			try:
				self.hover.mouseOut(self)
			except AttributeError:
				pass
			self.hover = hover

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
				painter.drawText(word.left, i * self.h - self.fm.descent(), str(word))

