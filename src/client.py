import socket
from json import dumps, loads
from base64 import b64encode
from time import time

from Transmission import (
	Serializer, 
	ClientMessage, 
	NewClientMessage, 
	EXIT,
	FILE, 
	CMD
)

class FileClient:
	def __init__(self):
		self.sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.port = 4000
		self.host = "localhost"
		self.header = 32
	
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
	
	def send(self, msg: bytes):

		MessageLengthAsInt = len(msg)
		
		if  len(str(MessageLengthAsInt)) <= self.header:
			# If the header is enough we send.
			
			MessageLengthAsBytes = self.PrepareMessageLengthToTransport(MessageLengthAsInt)
			self.sock.send(MessageLengthAsBytes)
			self.sock.send(msg)
			
			return

		print("Header is too small for msg!")

	def PrepareMessageLengthToTransport(self, m: int) -> bytes: 
		return Serializer.Encode_UTF8(str(m) + " " * (self.header - len(str(m))))

	def SendFileBytes(self, File_sender):
		
		if not File_sender.chunked:
			File_sender.send(self.sock, (lambda : self.HoldForResult(File_sender)))
			return

	def close(self):
		self.sock.close()
	
	def SendFile(self, File_sender):
		c = NewClientMessage(File_sender.FileInformationHeader(self.pwd))
		
		self.send(Serializer.SerializeClientMessage(c))
		self.SendFileBytes(File_sender)
		
		return

	def SendCmd(self, command: str):
		
		c = NewClientMessage({
			"pwd": self.pwd,
			"cmd": command
		}, CMD)

		self.send(Serializer.SerializeClientMessage(c))
		return

	def SendCloseServerCommand(self):
		self.SendCmd(EXIT)
		self.HoldForResult()

	def sendFileChunk(self, chunk: bytes, size: int):
		padding = " " * (self.header - len(str(size)))
		self.sock.send(Serializer.Encode_UTF8(str(size) + padding))
		self.sock.send(chunk)

	def SendFileBuffered(self, FileBlobObject): 
		for chunk in FileBlobObject: self.sendFileChunk(chunk.content, chunk.size)

	def HoldForResult(self, sentFile=None):
		Length_ = Serializer.Decode_UTF8(self.sock.recv(self.header))
		if Length_:
			ParsedLen = int(Length_.strip())
			if ParsedLen > 0:
				Resp = Serializer.DeserializeServerReponse(self.sock.recv(ParsedLen))
				Resp.Log()