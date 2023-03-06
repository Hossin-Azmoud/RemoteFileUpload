from base64 import b64encode, b64decode
from json import dumps
from pathlib import Path
from dataclasses import dataclass
CHUNK_SIZE = 1024 # IN BYTES.

class Bounds:

	def __init__(self, Tail: int=0, Head: int=1):
		self.Tail = Tail
		self.Head = Head

	@property
	def size_in_between(self):
		return abs(self.Tail - self.Head)

	def __add__(self, other):
		if isinstance(other, int):
			self.Head = self.Head + other
			self.Tail = self.Tail + other
		return self

	def __str__(self):
		return f'Bounds(Tail: {self.Tail}, Head: {self.Head})'

	def __repr__(self):
		return self.__str__()


@dataclass
class Chunk:
	content: bytes
	size: int


class FileSender:

	def __init__(self, fn, chunked = False) -> None:
		self.chunked = chunked
		self.fileObject = Path(fn)
		self.bytes = b64encode(self.fileObject.read_bytes())
		self.fn = self.fileObject.name
		self.size = len(self.bytes)
		self.Fileboundz: Bounds = Bounds(Tail = 0, Head = CHUNK_SIZE)

	def send(self, sock, callback):
		sock.send(self.bytes)
		callback()

	def FileInformationHeader(self, pwd) -> dict:
		
		if self.chunked:
			return {
				"fn": self.fn,
				"length": self.size,
				"pwd": pwd,
				"buf": 1
			}

		return {
			"fn": self.fn,
			"length": self.size,
			"pwd": pwd
		}

	
	def __iter__(self):
		return self
		

	def __next__(self):
		
		rest = self.size % CHUNK_SIZE
		TailCursor, HeadCursor = (self.Fileboundz.Tail, self.Fileboundz.Head)
		
		if (HeadCursor + CHUNK_SIZE < self.size - rest):
			self.Fileboundz += CHUNK_SIZE
			return Chunk(
				content=self.bytes[self.Fileboundz.Tail : self.Fileboundz.Head], 
				size=self.Fileboundz.size_in_between
			)
			
		if (HeadCursor + rest < self.size):
			self.Fileboundz.Tail += CHUNK_SIZE
			self.Fileboundz.Head += rest
			return Chunk(
				content=self.bytes[self.Fileboundz.Tail : self.Fileboundz.Head], 
				size=self.Fileboundz.size_in_between
			)
	
		raise StopIteration

class FileReceiver:
	def __init__(self, fn=None, size=0) -> None:	
		self.fn = fn
		self.size = size
		self.Buffer = b''
		

	def SetProperties(self, fn: str, size: int):
		self.SetFn(fn)
		self.SetSize(size)

	def SetFn(self, new: str) -> str:
		self.fn = new.replace("./", "").replace(".\\", "")
		return new

	def SetSize(self, new: int) -> int: 
		self.size = new
		return new

	def writeBuff(self, out_path):
		with open(self.make_path(out_path), "wb") as fp: 
			fp.write(self.Buffer)

	def DecodeReceivedBuff(self): self.Buffer = b64decode(self.Buffer)
	
	def ReceiveFileBuff(self, Conn, output_path, callback):
		
		self.Buffer = Conn.recv(self.size)
		
		if self.Buffer and self.fn:
			self.DecodeReceivedBuff()
			self.writeBuff(output_path)

		callback()

	def make_path(self, out_dir):
		delim = "/"
		out_dir = out_dir.replace("\\", delim)
		return delim.join([out_dir, self.fn])
	