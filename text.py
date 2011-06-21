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

	def __str__(self):
		return ''

gray = (150, 150, 150)
blue = (0, 60, 200)
green = (0, 200, 60)
orange = (255, 176, 31)

