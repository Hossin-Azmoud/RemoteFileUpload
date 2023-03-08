import socket
from threading import Thread, active_count
from dataclasses import dataclass, field
from json import dumps, loads
from base64 import b64decode
from hashlib import sha256
from ServerAuth import ConstructAuthManager
from datetime import datetime
from os import path
from Config import RFUConfig
from FileHandler import FileReceiver

from Transmission import (
	Serializer,
	ClientMessage,
	OKResp,
	ErrorResp,
	EXIT,
	FILE, 
	CMD,
	OK,
	NOT_OK
)


class Client:
	def __init__(self, conn, address, port):
		
		self.connected: bool = True
		self.Conn = conn
		self.Port = port
		self.Addr = address

	def disconnect(self):
		self.connected = False

class FileServer:	
	
	def __init__(self) -> None:
		
		self.ConfigInstance 	   =  RFUConfig()
		self.AuthManager    	   =  ConstructAuthManager(self.ConfigInstance)
		self.FileReceiver  	   	   =  FileReceiver()
		self.port       		   = 4000
		self.ServerHost 		   = socket.gethostbyname(socket.gethostname())
		self.sock       		   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.header     		   = 32
		self.isOpen                = True
	
	def SetHost(self, host):  self.ServerHost = host
	def SetPort(self, NewPort): self.port = NewPort

	def RecvChunks(self, Conn, address, length, fn):
		
		recv_byte_len = 0
		initializedFile = False
		tmp_buffer = b''

		while (recv_byte_len < length):

			ChunkSize = int(Serializer.Decode_UTF8(Conn.recv(self.header)).strip())
			tmp_buffer += Conn.recv(ChunkSize)
			recv_byte_len += ChunkSize

		self.DumpBytes(fn, tmp_buffer)
		self.OK(Conn)

	def kill(self): 
		self.close()

	def ExecuteCommand(self, Client_, c: str) -> None:
		if c == EXIT:
			self.sendResult(Client_, OK, "EXIT command executed!")
			self.kill()
		else:			
			self.sendResult(Client_, NOT_OK, "Unknown Command!")


	def sendResult(self, Client_, Code, Text=None):	
		
		if Code == OK: 
			self.send( Client_.Conn, OKResp(T=Text) )

		elif Code == NOT_OK: 
			self.send( Client_.Conn, ErrorResp(T=Text) )
		else: 
			self.send( Client_.Conn, NewServerResponse(T=Text, C=Code) )

		Client_.disconnect()

	def ProcessClientMessage(self, Message: ClientMessage, Client_) -> None:
	
		if Message.Type == FILE:
			if not Message.Chunked:
				# self.recvFileBlob(conn, address, length, fn)
				print("receivig file from ", Client_.Addr)
				print("File Name: ", Message.fn)
				print("Length: ", Message.length)
			
				self.FileReceiver.SetProperties(Message.fn, Message.length)
				self.FileReceiver.ReceiveFileBuff(Client_.Conn, self.ConfigInstance.SavePath, (lambda : self.sendResult(Client_, OK)))

			else:
				# TODO: Make buffreceiver. for chunked data.
				self.RecvChunks(Client_.Conn, Client_.Addr, Message.length, Message.fn)
			
			return

		if Message.Type == CMD:
			self.ExecuteCommand(Client_, Message.command)
			return
	
		self.sendResult(Client_.Conn, NOT_OK, f"""
			Invalid header msg, should be: pwd: ..., fn: ..., length: ...
			Instead received keys: { Message.Data }
		""")


	def connect(self, Client_):
		
		while Client_.connected:
			FileHeaderLength = Serializer.Decode_UTF8(Client_.Conn.recv(self.header))
			
			if FileHeaderLength:
				
				ParsedLen = int(FileHeaderLength.strip())
				
				if ParsedLen > 0:
					CMessage = Serializer.DeserializeClientMessage(Client_.Conn.recv(ParsedLen))
					CMessage.UnPackMessageData()
					
					if self.AuthManager.CheckPassword(CMessage.pwd):  
						self.ProcessClientMessage(CMessage, Client_)
						continue

					self.sendResult(Client_, NOT_OK, "Wrong password!")
					continue

					self.sendResult(Client_, NOT_OK, "Empty dataFrame!")

				continue

			self.sendResult(Client_, NOT_OK, "Sent empty header!")

	def send(self, Conn, msg):
		if not isinstance(msg, bytes):
			msg = Serializer.Encode_UTF8(msg)
		
		MessageLengthAsInt = len(msg)
		
		if  len(str(MessageLengthAsInt)) <= self.header:
			padding = " " * (self.header - len(str(MessageLengthAsInt)))
			Conn.send(Serializer.Encode_UTF8(str(MessageLengthAsInt) + padding))
			Conn.send(msg)
			return

		print("Header is too small for msg!")

	def Listen(self):
		
		self.bind_()
		
		with self.sock as Sock:
			Sock.listen(10)
			print(f"Server Started { self.ServerHost }:{ self.port }")
		
			while True:
				
				
				if self.isOpen:
					try:
						conn, connectInformation = Sock.accept()
						address, port = connectInformation
						C = Client(conn, address, port)		
						Thread_ = Thread(target=self.connect, args=(C, ))
						Thread_.start()
					
					except OSError as e:
						print("CLOSED")

					except Exception as e:
						print(e)

					continue

				break
				
	def bind_(self): self.sock.bind((self.ServerHost, self.port))
	
	def close(self): 
		self.isOpen = False
		print("Closing!")
		print(self.isOpen)
		self.sock.close()
