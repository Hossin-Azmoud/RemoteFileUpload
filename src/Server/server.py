import socket
from threading import Thread, active_count
from dataclasses import dataclass, field
from json import dumps, loads
from base64 import b64decode
from hashlib import sha256
from .Auth import ConstructAuthManager
from datetime import datetime
from os import path
UnitMap = {
	'B': 1024 ** 0,
	'KB': 1024 ** 1,
	'MB': 1024 ** 2,
	'GB': 1024 ** 3
}

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
	
def Ok(T: str = "OK"): 
	return ServerResponse(200, T).JSON()

def Error(T: str = "FAILED"): 
	return ServerResponse(404, T).JSON()

def DecodeClientMessage(ClientMessage: str):
	New = loads(ClientMessage)

	if ("fn" in New) and ("length" in New) and ("pwd" in New): 
		return (
			New["fn"], 
			New["length"], 
			New["pwd"], 
			"buf" in New
		)

	return False

@dataclass
class server:
	# clients: list = field(default_factory=list)
	
	PORT: int = 4000
	SERVER: str = socket.gethostbyname(socket.gethostname())
	SOCKET: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	HEADER: int = 32
	FORMAT: str = "utf-8"
	DISCONNECTING: str = "!DISCONNECT"

	def SetConfigInstance(self, configClass):
		self.AuthManager = ConstructAuthManager(configClass)
		self.configClass = configClass
	
	def resetPassword(self, newPassword):
		self.AuthManager
	def SetHost(self, host): 
		self.SERVER = host

	def SetPort(self, NewPort):
		self.PORT = NewPort

	def RecvChunks(self, Conn, address, length, fn):
		
		recv_byte_len = 0
		initializedFile = False
		tmp_buffer = b''

		while (recv_byte_len < length):
			
			print(f"RECV: { recv_byte_len } | ALL: { length }", end="\r")
			ChunkSize = int(Conn.recv(self.HEADER).decode(self.FORMAT).strip())
			tmp_buffer += Conn.recv(ChunkSize)
			recv_byte_len += ChunkSize

		self.DumpBytes(fn, tmp_buffer)
		self.send(Conn, Ok())

	def DumpBytes(self, fn, bytes_, mode='wb'):
		with open(self.configClass.joinWithSavePath(fn), mode) as f:
			print(f" { fn } -> { self.configClass.joinWithSavePath(fn) } ")
			f.write(b64decode(bytes_))

	def recvFileBlob(self, Conn, address, length, fn):

		print()
		print("Receiving content from (", address, ")")
		print("File Name: ", fn)
		print("content-length: ", GetSizeInProperUnit(length))
		
		Filebytes = Conn.recv(length)
		self.DumpBytes(fn, Filebytes)
		self.send(Conn, Ok())




	def connect(self, conn, clientInfo):
		address, port = clientInfo
		connected = True
		
		while connected:
			
			FileHeaderLength = conn.recv(self.HEADER).decode(self.FORMAT)
			
			if FileHeaderLength:
				ParsedLen = int(FileHeaderLength.strip())
								
				if ParsedLen > 0:
					Data_ = conn.recv(ParsedLen).decode(self.FORMAT)
					ClientMsg = DecodeClientMessage(Data_)
				
					if ClientMsg:
						fn, length, pwd, buf = ClientMsg

						if self.AuthManager.CheckPassword(pwd):
							if not buf:
								self.recvFileBlob(conn, address, length, fn)
								connected = False
							else:
								# TODO: Make buffreceiver. for chunked data.
								self.RecvChunks(conn, address, length, fn)
								connected = False
						else:
							self.send(conn, Error("Wrong password!"))	
							connected = False
						
					else:
						self.send(conn, Error(f"""
							Invalid header msg, should be: pwd: ..., fn: ..., length: ...
							Instead received keys: { Data_ }
						"""))
						connected = False
				else:
					self.send(conn, Error("Empty dataFrame!"))
					connected = False
			else:
				try:
					self.send(conn, Error("Sent empty header!"))
				except:
					pass

	def send(self, Conn, msg):
		
		MessageLengthAsInt = len(msg)	
		
		if  len(str(MessageLengthAsInt)) <= self.HEADER:
			padding = " " * (self.HEADER - len(str(MessageLengthAsInt)))
			Conn.send((str(MessageLengthAsInt) + padding).encode(self.FORMAT))
			Conn.send(msg.encode(self.FORMAT))
			return

		print("Header is too small for msg!")

	def Listen(self):
		self.bind_()
		
		with self.SOCKET as Sock:
			Sock.listen(10)	
			print(f"Server Started {self.SERVER}:{self.PORT}")

			while True:
				conn, clientInfo = Sock.accept()
				Thread_ = Thread(target=self.connect, args=(conn, clientInfo))
				Thread_.start()


	def bind_(self):
		self.SOCKET.bind((self.SERVER, self.PORT))

	def close(self):
		self.SOCKET.close()