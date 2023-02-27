import socket
from dataclasses import dataclass
from json import dumps, loads
from base64 import b64encode
from .File import FileBlob

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
			print("sent ->", str(MessageLengthAsInt) + padding, '|')
			self.SOCKET.send(msg.encode(self.FORMAT))
			return

		print("Header is too small for msg!")

	def SendDirect(self, bytes_): 
		self.SOCKET.send(bytes_)
		self.HoldForResult()

	def close(self):
		self.SOCKET.close()
	
	def SendFile(self, fn):
		""" {  } """
		with open(fn, "rb") as fp:
			FileBlobObject = FileBlob(fp)
			FileBlobObject.SendHeader(self)
			FileBlobObject.SendBytes(self.SendDirect)

	def HoldForResult(self):
		Length_ = self.SOCKET.recv(self.HEADER).decode(self.FORMAT)
		
		if Length_:
			ParsedLen = int(Length_.strip())
			if ParsedLen > 0:
				Data_ = self.SOCKET.recv(ParsedLen).decode(self.FORMAT)
				LoadedResult = loads(Data_)
				if LoadedResult["code"] == 200:
					print("Success")
					print(LoadedResult["text"])
				else:
					print("Failed! an error accured.")
					print(LoadedResult["text"])