import socket
from threading import Thread, active_count
from dataclasses import dataclass, field
from json import dumps, loads
from base64 import b64decode
from hashlib import sha256
from .Auth import ConstructAuthManager
from datetime import datetime
from os import path

# Size units.
UnitMap = {
	'B': 1024 ** 0,
	'KB': 1024 ** 1,
	'MB': 1024 ** 2,
	'GB': 1024 ** 3
}
# https://www.youtube.com/watch?v=p6xqKJqsQWs -> LISTEN WHILE CODING.
# My enums and constants.
OK = 200
OK_TEXT = "OK"
NOT_OK = 404
NOT_OK_TEXT = "FAILED"
SERVER_ERR = 500
SERVER_ERR_TEXT = "Unexpected error from socket server."

def GetSizeInProperUnit(ByteLen: int) -> str:
	Unit = 'B'

	if ByteLen < UnitMap['KB']:
		Unit = 'B'

	if UnitMap['KB'] <= ByteLen < UnitMap['MB']:
		Unit = 'KB'

	if UnitMap['MB'] <= ByteLen < UnitMap['GB']:
		Unit = 'MB'

	if ByteLen >= UnitMap['GB']:
		Unit = 'GB'

	return f'{ ByteLen / UnitMap[Unit] } { Unit }'

@dataclass
class ServerResponse:
	code: int
	text: str

	def __dict__(self): return {"code": self.code, "text": self.text}
	def JSON(self): return dumps(self.__dict__())


def DecodeClientMessage(ClientMessage: str):
	New = loads(ClientMessage)

	if ("fn" in New) and ("length" in New) and ("pwd" in New): 
		return (
			New["fn"], 
			New["length"], 
			New["pwd"], 
			"buf" in New
		)

	if ("Folder" in New) and ("length" in New) and ("pwd" in New):
		return New["Folder"], New["length"], New["pwd"]

	return False


class server:
	
	def __init__(self, FileReceiverInstance, ConfigInstance) -> None:
		self.AuthManager    	   =  ConstructAuthManager(ConfigInstance)
		self.ConfigInstance 	   =  ConfigInstance
		self.FileReceiver  	   =  FileReceiverInstance
		self.port       		   = 4000
		self.ServerHost 		   = socket.gethostbyname(socket.gethostname())
		self.sock       		   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.header     		   = 32
		self.encoding_format       = "utf-8"

	def SetHost(self, host):  self.ServerHost = host
	def SetPort(self, NewPort): self.port = NewPort

	def RecvChunks(self, Conn, address, length, fn):
		
		recv_byte_len = 0
		initializedFile = False
		tmp_buffer = b''

		while (recv_byte_len < length):

			ChunkSize = int(Conn.recv(self.header).decode(self.encoding_format).strip())
			tmp_buffer += Conn.recv(ChunkSize)
			recv_byte_len += ChunkSize

		self.DumpBytes(fn, tmp_buffer)
		self.OK(Conn)

	def OK(self, Conn): self.sendResult(Conn, OK)
	def Error(self, Conn): self.sendResult(Conn, NOT_OK)

	def sendResult(self, Conn, Code, Text=None):
		
		if Code == OK:
			self.send(Conn, 
				ServerResponse(
					code=OK, 
					text=(lambda : OK_TEXT if not Text else Text)()
				).JSON()
			)

		elif Code == NOT_OK:
			self.send(Conn, 
				ServerResponse(
					code=NOT_OK, 
					text=(lambda : NOT_OK_TEXT if not Text else Text)()
				).JSON()
			)
		
		else:
			self.send(Conn, 
				ServerResponse(
					code=SERVER_ERR, 
					text=SERVER_ERR_TEXT
				).JSON()
			)

	def connect(self, conn, clientInfo):
		
		address, port = clientInfo
		connected = True
		while connected:
			
			FileHeaderLength = conn.recv(self.header).decode(self.encoding_format)
			
			if FileHeaderLength:
				ParsedLen = int(FileHeaderLength.strip())

				if ParsedLen > 0:
					Data_ = conn.recv(ParsedLen).decode(self.encoding_format)
					
					ClientMsg = DecodeClientMessage(Data_)
									
					if ClientMsg:
						fn, length, pwd, buf = ClientMsg

						if self.AuthManager.CheckPassword(pwd):
							if not buf:
								# self.recvFileBlob(conn, address, length, fn)
								print("receivig file from ", address)
								print("File Name: ", fn)
								print("Length: ", length)
							
								self.FileReceiver.SetProperties(fn, length)
								self.FileReceiver.ReceiveFileBuff(conn, self.ConfigInstance.SavePath, (lambda : self.OK(conn)))
								connected = False
							else:
								# TODO: Make buffreceiver. for chunked data.
								self.RecvChunks(conn, address, length, fn)
								connected = False
						else:
							self.sendResult(conn, NOT_OK, "Wrong password!")
							connected = False
					else:
						self.sendResult(conn, NOT_OK, f"""
							Invalid header msg, should be: pwd: ..., fn: ..., length: ...
							Instead received keys: { Data_ }
						""")
						
						connected = False
				else:
					self.sendResult(conn, NOT_OK, "Empty dataFrame!")
					connected = False
			else:
				try:
					self.sendResult(conn, NOT_OK, "Sent empty header!")
				except:
					pass

	def send(self, Conn, msg):
		
		MessageLengthAsInt = len(msg)	
		
		if  len(str(MessageLengthAsInt)) <= self.header:
			padding = " " * (self.header - len(str(MessageLengthAsInt)))
			Conn.send((str(MessageLengthAsInt) + padding).encode(self.encoding_format))
			Conn.send(msg.encode(self.encoding_format))
			return

		print("Header is too small for msg!")

	def Listen(self):
		self.bind_()
		
		with self.sock as Sock:
			Sock.listen(10)	
			print(f"Server Started {self.ServerHost}:{self.port}")

			while True:
				conn, clientInfo = Sock.accept()
				Thread_ = Thread(target=self.connect, args=(conn, clientInfo))
				Thread_.start()


	def bind_(self):
		self.sock.bind((self.ServerHost, self.port))

	def close(self):
		self.sock.close()