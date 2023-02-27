from base64 import b64encode
from json import dumps

class FileBlob:
	
	def __init__(self, fp) -> None:
		self.FilePointer = fp
		self.fn = fp.name.replace('\\', '/').split('/')[-1]
		self.bytes = fp.read()

	@property
	def size(self): return len(self.bytes)

	# def StreamToSocket(self, seg, Conn):
	# 	...

	def SendHeader(self, SenderObj):
		SenderObj.send({
			"fn": self.fn,
			"length": self.size,
			"pwd": SenderObj.pwd
		})

	def SendBytes(self, sendCall):
		sendCall(self.bytes)







