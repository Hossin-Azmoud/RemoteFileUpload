import socket
from threading import Thread, active_count
from dataclasses import dataclass, field
from json import dumps, loads
from hashlib import sha256
Server_Key = sha256("01234567".encode()).hexdigest()

def CheckPassword(P: str): return (Server_Key == sha256(P.encode()).hexdigest())

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
		
		return New["fn"], New["length"], New["pwd"]
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

	def connect(self, conn, address):
		print(f"NEW CONNECTION: { address }")
		
		connected = True
		
		while connected:
			
			FileHeaderLength = conn.recv(self.HEADER).decode(self.FORMAT)

			if FileHeaderLength:
				ParsedLen = int(FileHeaderLength.strip())
				
				if ParsedLen > 0:
					Data_ = conn.recv(ParsedLen).decode(self.FORMAT)
					ClientMsg = DecodeClientMessage(Data_)
				
					if ClientMsg:
						fn, length, pwd = ClientMsg

						if CheckPassword(pwd):


							Filebytes = conn.recv(length)
						
							with open(fn, "wb") as f:
								print(f"To disk -> {fn}!")
								f.write(Filebytes)

							self.send(conn, Ok())
						else:
							self.send(conn, Error("Wrong password!"))	
						
					else:
						self.send(conn, Error(f"""
							Invalid header msg, should be: pwd: ..., fn: ..., length: ...
							Instead received keys: { Data_ }
						"""))
				else:
					self.send(conn, Error("Empty dataFrame!"))
			else:
				self.send(conn, Error("Sent empty header!"))

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
				conn, address = Sock.accept()
				Thread_ = Thread(target=self.connect, args=(conn, address))
				Thread_.start()


	def bind_(self):
		self.SOCKET.bind((self.SERVER, self.PORT))

	def close(self):
		self.SOCKET.close()
 
