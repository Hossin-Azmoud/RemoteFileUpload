from base64 import b64encode
from json import dumps
from pathlib import Path

CHUNK_SIZE = 1024 # IN BYTES.

class FileBlob:

	def __init__(self, fn, chunked = False) -> None:
		self.chunked = chunked
		self.fileObject = Path(fn)
		self.bytes = b64encode(self.fileObject.read_bytes())
		self.fn = self.fileObject.name
		self.size = len(self.bytes)

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
		
		currentChunk = [0, CHUNK_SIZE]
		yielded = 0
		rest = self.size - (self.size % CHUNK_SIZE)
		
		while yielded < self.size:
			yield (self.bytes[currentChunk[0] : currentChunk[1]], yielded, )
			currentChunk[0] += CHUNK_SIZE
			currentChunk[1] += CHUNK_SIZE


