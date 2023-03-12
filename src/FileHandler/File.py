from base64 import b64encode, b64decode
from json import dumps
from pathlib import Path
from dataclasses import dataclass
from os import stat

OK = 200
PARSE_ERROR = 501
NOT_OK = 404

HEADER = 16
FORMAT = "utf-8"
CHUNK_SIZE = (1024 * 1024 * 4) # IN BYTES.


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
	size: int
	
	def EncodeB64(self):
		self.content = b64encode(self.content)
		self.size = len(self.content)

	def DecodeB64(self):
		
		missing_padding = len(self.content) % 4		
		if missing_padding:	self.content += b'=' * (4 - missing_padding)

		self.content = b64decode(self.content)
		self.size = len(self.content)

	def Fill(self, data: bytes, size: int):
		self.content = data
		self.size = size

	def Free(self):
		self.content = b''
		self.size = 0

	def __str__(self):
		return f'chunk: ... size: {self.size}'


class FileSender:

	def __init__(self, fn, chunked = False) -> None:
		
		self.chunked = chunked
		self.PathObject = Path(fn)
		self.fn = self.PathObject.name
		self.size = stat(self.PathObject).st_size

	def send(self, sock, callback):
		with open(self.PathObject, "rb") as fp:
			sock.send(fp.read())
			callback()

	def LogInformation(self, Logger):
		Logger.inform(f"File Name: {self.fn}.")
		Logger.inform(f"Size: {self.size}.")
		Logger.inform(f"Abs path: {self.PathObject}.")

	def sendChunks(self, chunkCapture: callable, progressCallback: callable):
		print()
		read = 0
		
		with open(self.PathObject, "rb") as fp: 		
			while read < (self.size - (self.size % CHUNK_SIZE)):
				# Read Chunk
				ChunkBytes = fp.read(CHUNK_SIZE)

				# encapsulate Chunk
				chunkObj = Chunk(ChunkBytes, CHUNK_SIZE)
				chunkObj.EncodeB64()
				
				# Send chunk to the caller
				chunkCapture(chunkObj)
				read += CHUNK_SIZE
				progressCallback(self.size, read)

			if (self.size % CHUNK_SIZE) > 0:
				ChunkBytes = fp.read(self.size % CHUNK_SIZE)
				chunkObj = Chunk(ChunkBytes, self.size % CHUNK_SIZE)
				chunkObj.EncodeB64()
				chunkCapture(chunkObj)

			read += self.size % CHUNK_SIZE
			progressCallback(self.size, read)

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
			fp.write(self.Buffer)
			self.Buffer = b''

	def DecodeReceivedBuff(self): self.Buffer = b64decode(self.Buffer)

	def Notify(self, Client_, Logger):
		Logger.inform(f"Upcoming File write from : { Client_.Addr }")
		Logger.inform(f"File Name : { self.fn }")
		Logger.inform(f"size : { self.size }")
		

	def ReceiveFileBuff(self, Client_, output_path, callback, Logger):
		self.Notify(Client_, Logger)
		self.Buffer = Client_.Conn.recv(self.size)
		
		if self.Buffer and self.fn:
		
			Logger.inform("Saving the file :3")
			self.writeBuff(output_path)
			Logger.success("saved!")

		callback()

	def ReceiveFileBuffChunked(self, Client_, output_path, callback, progressCallback, Logger):
		

		self.Notify(Client_, Logger)
		received = 0
		progressCallback(self.size, received)
		result = (lambda c : Client_.Conn.send(str(c).encode(FORMAT)))
		
		while (received < self.size):

			try:
				
				Size_inBytes = Client_.Conn.recv(HEADER)
				ChunkSize_b64 = int(Size_inBytes.decode("utf-8").strip())

			except ValueError:
				# resend Chunk.
				Logger.error("Incorrect size: " + Size_inBytes.decode('utf-8'))
				result(PARSE_ERROR)
				continue
			
			except Exception as e:
				# resend Chunk.
				Logger.inform("Error while receiving the size of the chunk.")
				Logger.error(e)
				result(NOT_OK)
				continue
			
			result(OK)
			RecvChunk_b64 = Client_.Conn.recv(ChunkSize_b64)
			chunkObj = Chunk(RecvChunk_b64, ChunkSize_b64)
			chunkObj.DecodeB64()
			received += chunkObj.size
			self.Buffer += chunkObj.content
			# Next Chunk.
			
			progressCallback(self.size, received)

		if self.Buffer and self.fn: 
			Logger.inform("Saving the file :3")
			self.writeBuff(output_path)
			Logger.success("saved!")

		callback()

	def make_path(self, out_dir):
		delim = "/"
		out_dir = out_dir.replace("\\", delim)
		return delim.join([out_dir, self.fn])