import socket
from json import dumps, loads
from base64 import b64encode
from time import time
from Util import Logger

from Transmission import (
	Serializer, 
	ClientMessage, 
	NewClientMessage, 
	EXIT,
	FILE,
	CMD
)

from FileHandler import Chunk, FileSender

class FileProtocolClient:
	def __init__(self):
		self.sock: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.port = 4000
		self.host = socket.gethostbyname(socket.gethostname())
		self.header = 32
		self.Logger = Logger()

	def SetHost(self, host: str):   	 
		self.host = host

	def SetPort(self, NewPort: int):	 
		self.port = NewPort

	def setPassword(self):     	 		 
		self.pwd = input(f"Type in password to connect to ({self.host}) :")

	def connect(self):
		if self.host:
			self.Logger.inform(f"Connection being established with: { self.host }")
			
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

		self.Logger.error("Header is too small for msg!")

	def PrepareMessageLengthToTransport(self, m: int) -> bytes: 
		return Serializer.Encode_UTF8(str(m) + " " * (self.header - len(str(m))))

	def SendFileBytes(self, File_sender: FileSender):
		
		File_sender.LogInformation(self.Logger)
		if not File_sender.chunked:		
			File_sender.send(self.sock, (lambda : self.HoldForResult(File_sender)))
			return

		self.Logger.inform(f"sending file using chunked protocol")
		self.SendFileBuffered(File_sender)
		self.HoldForResult(File_sender)
	
	def close(self): self.sock.close()
	
	def SendFile(self, File_sender: FileSender):
		c = NewClientMessage(File_sender.FileInformationHeader(self.pwd))
		self.send(Serializer.SerializeClientMessage(c))
		self.Logger.inform(f"File information sent")
		self.SendFileBytes(File_sender)

	def SendCmd(self, command: str):
		
		c = NewClientMessage({
			"pwd": self.pwd,
			"cmd": command
		}, CMD)

		self.Logger.inform(f"sending Command: {command}")
		self.send(Serializer.SerializeClientMessage(c))

	def SendCloseServerCommand(self):
		self.SendCmd(EXIT)
		self.HoldForResult()

	def sendFileChunk(self, chunk: Chunk):
		# Implement a progress bar.
		padding = " " * (self.header - len(str(chunk.size)))
		EncodedCSize = Serializer.Encode_UTF8(str(chunk.size) + padding)
		self.sock.send(EncodedCSize)
		self.sock.send(chunk.content)


	def SendFileBuffered(self, File_sender: FileSender): 
		self.temp = File_sender
		File_sender.sendChunks(self.sendFileChunk)

	def HoldForResult(self, sentFile: FileSender | None=None):
		Length_ = Serializer.Decode_UTF8(self.sock.recv(self.header))
		
		if Length_:
			ParsedLen = int(Length_.strip())
			if ParsedLen > 0:
				Resp = Serializer.DeserializeServerReponse(self.sock.recv(ParsedLen))
				if Resp.code == 200:
					
					if sentFile:
						self.Logger.inform(f"{ sentFile.fn } was sent to { self.host }")
						return

					self.Logger.inform()
					return
				
				self.Logger.error(f"{ sentFile.fn } was not sent successfully.")