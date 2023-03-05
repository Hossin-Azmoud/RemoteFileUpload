import socket
from dataclasses import dataclass
from json import dumps, loads
from base64 import b64encode
from .File import FileBlob
from time import time

@dataclass
class Client:
	PORT: int = 4000
	SERVER: str = None
	SOCKET: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	HEADER: int = 32
	DISCONNECTING: str = "!DISCONNECT"
	FORMAT: str = "utf-8"

	def SetHost(self, host):
		self.SERVER = host

	def SetPort(self, NewPort):
		self.PORT = NewPort

	def setPassword(self):
		p = input(f"Type in password to connect to ({self.SERVER}) :")
		self.pwd = p

	def connect(self):
		""" connects to a host! """
		
		if self.SERVER:
			print(f"CONNECTING TO -> { self.SERVER }")
			self.SOCKET.connect((
				self.SERVER, self.PORT
			))
	
	def send(self, msg):
		
		if not isinstance(msg, str):
			msg = dumps(msg)

		MessageLengthAsInt = len(msg)	
		if  len(str(MessageLengthAsInt)) <= self.HEADER:
			padding = " " * (self.HEADER - len(str(MessageLengthAsInt)))
			self.SOCKET.send((str(MessageLengthAsInt) + padding).encode(self.FORMAT))
			self.SOCKET.send(msg.encode(self.FORMAT))
			return

		print("Header is too small for msg!")


	def SendFileBytes(self, FileBlobObject):
		
		if not FileBlobObject.chunked:
			self.SOCKET.send(FileBlobObject.bytes)
			self.HoldForResult(FileBlobObject)
			return

		self.SendFileBuffered(FileBlobObject)
		self.HoldForResult(FileBlobObject)

	def close(self):
		self.SOCKET.close()
	
	def SendFile(self, fn, chunked_flag=False):
		FileBlobObject = FileBlob(fn, chunked = chunked_flag)
		self.send(FileBlobObject.FileInformationHeader(self.pwd))
		self.SendFileBytes(FileBlobObject)
		return


	def sendFileChunk(self, chunk: bytes, size: int):
		padding = " " * (self.HEADER - len(str(size)))
		self.SOCKET.send((str(size) + padding).encode(self.FORMAT))
		self.SOCKET.send(chunk)

	def SendFileBuffered(self, FileBlobObject):		
		for chunk in FileBlobObject: self.sendFileChunk(chunk.content, chunk.size)

	def HoldForResult(self, sentFile):
		Length_ = self.SOCKET.recv(self.HEADER).decode(self.FORMAT)
		
		if Length_:
			ParsedLen = int(Length_.strip())
			if ParsedLen > 0:
				Data_ = self.SOCKET.recv(ParsedLen).decode(self.FORMAT)
				LoadedResult = loads(Data_)
				
				if LoadedResult["code"] == 200:
					print()
					print(f"({sentFile.fn}):{sentFile.size} -> { self.SERVER }")
					print(f"Sent!")

				else:
					print()
					print(f"File {sentFile.fn} was not sent.")
					print("Error log:", LoadedResult["text"])
					