from base64 import b64encode
from json import dumps

class FileSender:
	def __init__(self, fp) -> None:
		self.FilePointer = fp
		self.fn = fp.name.replace('\\', '/').split('/')[-1]
		self.bytes = b64encode(fp.read())

	def SendBuffered(self, buffSize: int):
		...

	@property
	def size(self): return len(self.bytes)

	def SendHeader(self, SenderObj):
		SenderObj.send({
			"fn": self.fn,
			"length": self.size,
			"pwd": SenderObj.pwd
		})

	def SendBytes(self, sendCall): 
		sendCall(self.bytes)



class FileReceiver:
	def __init__():
		...

	def 