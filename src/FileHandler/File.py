from base64 import b64encode, b64decode
from json import dumps
from pathlib import Path
from dataclasses import dataclass
from os import stat
CHUNK_SIZE = 1024 # IN BYTES.

class Bounds:

	def __init__(self, Tail: int=0, Head: int=1):
		self.Tail = Tail
		self.Head = Head

	@property
	def size_in_between(self):
		return abs(self.Head - self.Tail)

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
	size:    int

	def EncodeB64(self):
		self.content = b64encode(self.content)
		self.size = len(self.content)

	def DecodeB64(self):
		self.content = b64decode(self.content)
		self.size = len(self.content)

class FileSender:

	def __init__(self, fn, chunked = False) -> None:
		
		self.chunked = chunked
		self.fileObject = Path(fn)
		self.fn = self.fileObject.name
		self.size = stat(self.fileObject).st_size

	def send(self, sock, callback):
		sock.send(self.bytes_)
		callback()

	def sendChunks(self, callback: callable):

		read = 0
		
		with open(self.fileObject, "rb") as fp: 

			while read < (self.size - (self.size % CHUNK_SIZE)):				
				# Read Chunk
				ChunkBytes = fp.read(CHUNK_SIZE)
				
				# encapsulate Chunk
				chunkObj = Chunk(content=ChunkBytes, size=CHUNK_SIZE)
				chunkObj.EncodeB64()
				callback(chunkObj)
				
				read += CHUNK_SIZE

			if (self.size % CHUNK_SIZE) > 0:
				ChunkBytes = fp.read(self.size % CHUNK_SIZE)
				
				chunkObj = Chunk(content=ChunkBytes, size=(self.size % CHUNK_SIZE))
				chunkObj.EncodeB64()
				callback(chunkObj)
				
			read += self.size % CHUNK_SIZE
			
			print("Finished Reading chunks.", self.size, read)


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
			print(f"\n{ self.fn } -> DISC ")
			fp.write(self.Buffer)
			self.Buffer = b''

	def DecodeReceivedBuff(self): self.Buffer = b64decode(self.Buffer)

	def Notify(self, Client_):
		print("Upcoming File write from : ", Client_.Addr)
		print("File Name : ", self.fn)
		print("Size : ", self.size)

	
	def ReceiveFileBuff(self, Client_, output_path, callback):
		self.Notify(Client_)
		self.Buffer = Client_.Conn.recv(self.size)
		
		if self.Buffer and self.fn:
			self.DecodeReceivedBuff()
			self.writeBuff(output_path)

		callback()

	def ReceiveFileBuffChunked(self, Client_, output_path, callback, onProgress):
		self.Notify(Client_)
		received = 0
		onProgress(received, self.size - received, self.size)
		
		while (received < self.size):

			ChunkSize_b64 = int(Client_.Conn.recv(32).decode("utf-8").strip())
			RecvChunk_b64 = Client_.Conn.recv(ChunkSize_b64)
			chunkObj = Chunk(content=RecvChunk_b64, size=ChunkSize_b64)
			chunkObj.DecodeB64()
			received += chunkObj.size
			self.Buffer += chunkObj.content
			
			onProgress(received, self.size - received, self.size)

		if self.Buffer and self.fn: self.writeBuff(output_path)

		callback()

	def make_path(self, out_dir):
		delim = "/"
		out_dir = out_dir.replace("\\", delim)
		return delim.join([out_dir, self.fn])
	