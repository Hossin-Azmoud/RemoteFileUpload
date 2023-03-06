import socket
from json import dumps, loads
from base64 import b64encode
from time import time

class Client:
	def __init__(self):
		self.sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.port = 4000
		self.host = "localhost"
		self.header = 32
		self.encoding_format = "utf-8"
	
	def SetHost(self, host):   	 self.host = host
	def SetPort(self, NewPort):	 self.port = NewPort
	def setPassword(self):     	 self.pwd = input(f"Type in password to connect to ({self.host}) :")
	def connect(self):
		""" connects to a host! """
		if self.host:
			print(f"CONNECTING TO -> { self.host }")
			self.sock.connect((
				self.host, self.port
			))
	
	def send(self, msg):
		
		if not isinstance(msg, str):
			msg = dumps(msg)

		MessageLengthAsInt = len(msg)	
		if  len(str(MessageLengthAsInt)) <= self.header:
			padding = " " * (self.header - len(str(MessageLengthAsInt)))
			self.sock.send((str(MessageLengthAsInt) + padding).encode(self.encoding_format))
			self.sock.send(msg.encode(self.encoding_format))
			return

		print("Header is too small for msg!")


	def SendFileBytes(self, File_sender):
		
		if not File_sender.chunked:
			File_sender.send(self.sock, (lambda : self.HoldForResult(File_sender)))
			return

	def close(self):
		self.sock.close()
	
	def SendFile(self, File_sender):
		self.send(File_sender.FileInformationHeader(self.pwd))
		self.SendFileBytes(File_sender)
		return


	def sendFileChunk(self, chunk: bytes, size: int):
		padding = " " * (self.header - len(str(size)))
		self.sock.send((str(size) + padding).encode(self.encoding_format))
		self.sock.send(chunk)

	def SendFileBuffered(self, FileBlobObject):		
		for chunk in FileBlobObject: self.sendFileChunk(chunk.content, chunk.size)

	def HoldForResult(self, sentFile):
		Length_ = self.sock.recv(self.header).decode(self.encoding_format)
		
		if Length_:
			ParsedLen = int(Length_.strip())
			if ParsedLen > 0:
				Data_ = self.sock.recv(ParsedLen).decode(self.encoding_format)
				LoadedResult = loads(Data_)
				
				if LoadedResult["code"] == 200:
					print()
					print(f"({sentFile.fn}):{sentFile.size} -> { self.host }")
					print(f"Sent!")

				else:
					print()
					print(f"File {sentFile.fn} was not sent.")
					print("Error log:", LoadedResult["text"])
					