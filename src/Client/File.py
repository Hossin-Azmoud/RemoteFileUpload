from base64 import b64encode
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


class FileBlob:

	def __init__(self, fn, chunked = False) -> None:
		self.chunked = chunked
		self.fileObject = Path(fn)
		self.bytes = b64encode(self.fileObject.read_bytes())
		self.fn = self.fileObject.name
		self.size = len(self.bytes)
		self.Fileboundz: Bounds = Bounds(Tail = 0, Head = CHUNK_SIZE)

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
