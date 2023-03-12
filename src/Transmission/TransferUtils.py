from json import loads, dumps
from dataclasses import dataclass

# https://www.youtube.com/watch?v=p6xqKJqsQWs -> LISTEN WHILE CODING.
# My enums and constants.

# Size units.
UNITMAP = {
	'B': 1024 ** 0,
	'KB': 1024 ** 1,
	'MB': 1024 ** 2,
	'GB': 1024 ** 3
}

DEFAULT_ENCODING  = "utf-8"

OK                = 200
OK_TEXT           = "OK"
NOT_OK            = 404
NOT_OK_TEXT 	  = "FAILED"
SERVER_ERR 		  = 500
SERVER_ERR_TEXT   = "Unexpected error from socket server."
FILE 			  = "FILE"
CMD  			  = "CMD"
EXIT              = "EXIT"

def GetSizeInProperUnit(ByteLen: int) -> str:

	Unit = 'B'
	if ByteLen < UNITMAP['KB']:
		Unit = 'B'

	if UNITMAP['KB'] <= ByteLen < UNITMAP['MB']:
		Unit = 'KB'

	if UNITMAP['MB'] <= ByteLen < UNITMAP['GB']:
		Unit = 'MB'

	if ByteLen >= UNITMAP['GB']:
		Unit = 'GB'

	return f'{ int(ByteLen // UNITMAP[Unit]) } { Unit }'

@dataclass
class ServerResponse:
	code: int
	text: str
	def __dict__(self): return { "code": self.code, "text": self.text }
	def JSON(self): return dumps(self.__dict__())
	
	def Log(self): 
		print("Server Sent a response:")
		print("code: ", self.code)
		print("text: ", self.text)

class ServerClient:
	def __init__(self, conn, address, port):
		
		self.connected: bool = True
		self.Conn = conn
		self.Port = port
		self.Addr = address

	def disconnect(self):
		self.connected = False


class ClientMessage:
	
	def __init__(self, Type: int=None, Data: str | dict=None) -> None:
		
		if not Type:
			Type = FILE

		self.Type = Type
		self.Data = Data
	
	def UnPackMessageData(self):
		self.pwd = self.Data["pwd"]
		
		if self.Type == FILE:
			self.fn = self.Data["fn"]
			self.length = self.Data["length"]
			self.Chunked = ("buf" in self.Data)
			return

		if self.Type == CMD:
			self.command = self.Data["cmd"]
			return 

	def __dict__(self) -> dict:	return { "Type": self.Type, "Data": self.Data }
	def __repr__(self) -> str: return f'{self.Type}\n {self.Data}'
	def __str__(self) -> str: return f'<{self.__class__.__name__} Type={ self.Type } />'
	

class Serializer:
	
	def DeserializeClientMessage(bytes_: bytes) -> ClientMessage:
		""" extract the info from bytes. """
		data = loads(bytes_.decode(DEFAULT_ENCODING))
		
		return ClientMessage(
			data["Type"],
			data["Data"]
		)

	def SerializeClientMessage(message: ClientMessage) -> bytes: 
	
		return dumps(message.__dict__()).encode(DEFAULT_ENCODING)
	
	def DeserializeServerReponse(Bytes: bytes) -> ServerResponse:
		data = loads(Bytes.decode(DEFAULT_ENCODING))
	
		return ServerResponse(
			code=data["code"],
			text=data["text"]
		)
	
	def SerializeServerReponse(response: ServerResponse) -> bytes: return response.JSON().encode(DEFAULT_ENCODING)
	
	def Encode_UTF8(s: str) -> bytes: return s.encode(DEFAULT_ENCODING)
	
	def Decode_UTF8(bytes_: bytes) -> str: 
		return bytes_.decode(DEFAULT_ENCODING)
		

def DecodeClientMessage(ClientMessage: bytes):
	if len(ClientMessage) > 0:
		ClientMessageInstance = Serial.Deserialize(ClientMessage)
		return ClientMessageInstance

	return False

# test.
def NewClientMessage(d, t=None):
	return ClientMessage(
		Data=d,
		Type=t,
	)

def NewServerResponse(T=OK_TEXT, C=OK):    return Serializer.SerializeServerReponse(ServerResponse(code=C, text=T))
def OKResp(T: str=None):           			   return NewServerResponse(T=T) if T else NewServerResponse()
def ErrorResp(T: str=None): 			   return NewServerResponse(T=(T if T else NOT_OK_TEXT), C=NOT_OK) 


def SerialTest():
	data = { "Type": "Hello", "Data": "World!" }
	ob = NewClientMessage(data["Data"], t=data["Type"])
	print(ob)
	ret  = Serial.Serialize(ob)
	# SendDataByClient(ret)
	print(ret)
	
	ret = Serial.Deserialize(ret)
	
	print(ret.Type)
	print(ret.Data)

def main():
	SerialTest()


if __name__ == '__main__':
	main()