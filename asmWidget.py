from PySide.QtCore import *
from PySide.QtGui import *
from text import *

class AsmArea(QAbstractScrollArea):
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
		self.hover = None
		self.scroll = 0

		self.verticalScrollBar().setSingleStep(self.h)


	def resizeEvent(self, event):
		self.updateContent()
		self.verticalScrollBar().setPageStep(self.height())

	def scrollContentsBy(self, dx, dy):
		self.scroll = self.verticalScrollBar().value()
		self.updateContent()

	def notify(self, subject):
		self.updateContent()

	def setContentSource(self, source):
		self.source = source
		source.addObserver(self)
		self.updateContent()

	def updateContent(self):
		line = self.scroll / self.h
		self.text = self.source.getText(line, self.height() / self.h + 1)
		for line in self.text:
			x = 5
			for word in line:
				word.left = x
				if type(word) is Tab:
					x = max(word.stop, x)
				else:
					x += self.fm.width(str(word))
				word.right = x
		self.viewport().update()
		self.verticalScrollBar().setPageStep(self.source.getTextSize() * self.h)
		self.verticalScrollBar().setRange(0, self.source.getTextSize() * self.h - self.height())

	def mouseMoveEvent(self, event):
		if not self.highlightLine == event.pos().y() / self.h:
			self.highlightLine = event.pos().y() / self.h
			self.viewport().update()
		x = event.pos().x()
		try:
			hover = filter(lambda w: w.left < x and w.right > x, self.text[self.highlightLine])[0]
		except IndexError:
			hover = None
		if hover is not self.hover:
			try:
				hover.mouseIn(self.viewport())
			except AttributeError:
				pass
			try:
				self.hover.mouseOut(self.viewport())
			except AttributeError:
				pass
			self.hover = hover

	def paintEvent(self, event):
		painter = QPainter(self.viewport())

		painter.fillRect(0, self.h * self.highlightLine - self.scroll % self.h, self.width(), self.h, self.palette().alternateBase())

		for i,line in enumerate(self.text, 1):
			for word in line:
				try:
					painter.setPen(QColor(*word.color))
				except AttributeError:
					painter.setPen(QColor(0, 0, 0))
				painter.drawText(word.left, i * self.h - self.fm.descent() - self.scroll % self.h, str(word))

