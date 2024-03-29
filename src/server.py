import socket
from time import time 
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
from Util import Logger, progressBar
from Transmission import (
    Serializer,
    ServerClient,
    ClientMessage,
    GetSizeInProperUnit,
    OKResp,
    ErrorResp,
    EXIT,
    FILE, 
    CMD,
    OK,
    NOT_OK
)

class FileProtocolServer:   
    
    def __init__(self) -> None:
        
        self.ConfigInstance        =  RFUConfig()
        self.AuthManager           =  ConstructAuthManager(self.ConfigInstance)
        self.FileReceiver          =  FileReceiver()
        self.Logger                =  Logger()
        self.port                  =  4000
        self.ServerHost            =  socket.gethostbyname(socket.gethostname())
        self.sock                  =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.header                =  16
        self.isOpen                =  True
        self.Timed                 = True

    def SetHost(self, host):  self.ServerHost = host
    def SetPort(self, NewPort): self.port = NewPort
    def kill(self): self.close()
    def bind_(self): self.sock.bind((self.ServerHost, self.port))
    def close(self):
        self.isOpen = False
        self.sock.close()

    def ExecuteCommand(self, Client_: ServerClient, c: str) -> None:
        if c == EXIT:
            self.sendResult(Client_, OK, "EXIT command executed!")
            self.kill()
        else:
            self.sendResult(Client_, NOT_OK, "Unknown Command!")


    def sendResult(self, Client_: ServerClient, Code: int, Text:str=None):  
        
        if Code == OK: 
            self.send( Client_.Conn, OKResp(T=Text) )

        elif Code == NOT_OK: 
            self.send( Client_.Conn, ErrorResp(T=Text) )
        else: 
            self.send( Client_.Conn, NewServerResponse(T=Text, C=Code) )

        Client_.disconnect()
    
    def SetTimer(self) -> None: self.Timed = True

    def ProcessClientMessage(self, Message: ClientMessage, Client_: ServerClient) -> None:
         
        if Message.Type == FILE:
            self.FileReceiver.SetProperties(Message.fn, Message.length)
            start = time()
            if not Message.Chunked: 

                self.FileReceiver.ReceiveFileBuff(Client_, self.ConfigInstance.SavePath, (lambda : self.sendResult(Client_, OK)), self.Logger)

                if self.Timed:
                    self.Logger.inform(f"received in: {time() - start} s")

                return
            
            self.FileReceiver.ReceiveFileBuffChunked(Client_, self.ConfigInstance.SavePath, (lambda : self.sendResult(Client_, OK)), progressBar, self.Logger)
            if self.Timed:
                self.Logger.inform(f"received in: {time() - start} s")
            return

        if Message.Type == CMD:
            self.ExecuteCommand(Client_, Message.command)
            return
        
        self.sendResult(Client_.Conn, NOT_OK, f"""
            Invalid header msg, should be: pwd: ..., fn: ..., length: ...
            Instead received keys: { Message.Data }
        """)


    def connect(self, Client_: ServerClient):
        
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
                    break

                self.sendResult(Client_, NOT_OK, "Empty dataFrame!")

                continue

            self.sendResult(Client_, NOT_OK, "Sent empty header!")

    def send(self, Conn, msg: bytes | str) -> None:
        
        if not isinstance(msg, bytes):
            msg = Serializer.Encode_UTF8(msg)
        
        MessageLengthAsInt = len(msg)
        
        if  len(str(MessageLengthAsInt)) <= self.header:
            padding = " " * (self.header - len(str(MessageLengthAsInt)))
            Conn.send(Serializer.Encode_UTF8(str(MessageLengthAsInt) + padding))
            Conn.send(msg)
            return

        self.Logger.error("Header is too small to send the message len.")

    def Listen(self):
        
        self.bind_()
        
        with self.sock as Sock:
            Sock.listen(10)
            self.Logger.inform(f"Server Started { self.ServerHost }:{ self.port }")
        
            while True:
                
                
                if self.isOpen:
                    try:
                        conn, connectInformation = Sock.accept()
                        # conn.setblocking(False)
                        address, port = connectInformation
                        C = ServerClient(conn, address, port)       
                        Thread_ = Thread(target=self.connect, args=(C, ))
                        Thread_.start()
                    
                    except OSError as e:
                        self.Logger.inform("Closed server.")

                    except Exception as e:
                        self.Logger.error(e)

                    continue

                break
