import struct

class Stream(object):
	""" This object provides an interface to a variable number of bytes 
		at a fixed offset in memory for processor modules to use. 

		It also takes care of endiness for larger reads. """
	def __init__(self, block, offset):
		self.block = block
		self.offset = offset
		self.count = 0

	def read8(self):
		byte = struct.unpack_from("<B", self.block, self.offset)[0]
		self.offset += 1
		self.count += 1
		return byte

	def read8s(self): # Signed read byte
		byte = struct.unpack_from("<b", self.block, self.offset)[0]
		self.offset += 1
		self.count += 1
		return byte

	def read16(self):
		short = struct.unpack_from("<H", self.block, self.offset)[0]
		self.offset += 2
		self.count += 2
		return short

