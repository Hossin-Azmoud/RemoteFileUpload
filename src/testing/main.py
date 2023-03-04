from random import randint
from base64 import b64encode
from json import dumps
from pathlib import Path
from dataclasses import dataclass


CHUNK_SIZE = 1024 # IN BYTES.
TESTING_FILE = './Testing.t'

@dataclass
class Bounds:
	Tail: int
	Head: int

	@property
	def size_in_between(self): 
		return abs(self.Tail - self.Head)

	def __add__(self, other):
		if isinstance(other, int):
			self.Head += other
			self.Tail += other



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
		Reachable = self.size - rest
		
		if (self.Fileboundz.Tail + CHUNK_SIZE) < Reachable:
			T, H = self.Fileboundz.Tail, self.Fileboundz.Head
			self.Fileboundz += CHUNK_SIZE
			return (self.bytes[T : H], CHUNK_SIZE)

		else:
			if rest > 0:
				r = rest
				rest = 0
				return (self.bytes[self.Fileboundz.Tail : self.Fileboundz.Head + r], r)

			else:
				raise StopIteration
		
		

def GenerateFile(size: int):
	
	with open(TESTING_FILE, 'wb') as fp:
		for i in range(size): 
			fp.write(
				chr(randint(0, 256))
				.encode()
			)

	print(size, 'bytes written to ', TESTING_FILE)

def main():
	GenerateFile(1283830)
	FileOb = FileBlob(TESTING_FILE)
	for i in FileOb:
		print(i)

if __name__ == '__main__':
	main()


