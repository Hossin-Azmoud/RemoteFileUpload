from base64 import b64encode, b64decode
from json import dumps
from pathlib import Path
from dataclasses import dataclass
from os import stat

OK = 200
PARSE_ERROR = 501
NOT_OK = 404
HEADER = 16
FORMAT = "utf-8"
CHUNK_SIZE = (1024 * 1024 * 4) # IN BYTES.

def GetChunkSizeAfterEncoded(chunk: bytes) -> int: 
    return len(b64encode(chunk))



class Bounds:

    def __init__(self, Tail: int=0, Head: int=1):
        self.Tail = Tail
        self.Head = Head

    @property
    def size_in_between(self): return abs(self.Head - self.Tail)

    def __add__(self, other):
        
        if isinstance(other, int):
        
            self.Head = self.Head + other
            self.Tail = self.Tail + other
        
        return self

    def __str__(self): return f'Bounds(Tail: {self.Tail}, Head: {self.Head})'
    def __repr__(self): return self.__str__()




class Chunk:
    
    def __init__(self, content: bytes):
        self.content = content
    
    def EncodeB64(self):
        self.content = b64encode(self.content)

    def DecodeB64(self):
        
        missing_padding = len(self.content) % 4
        if missing_padding: 
            self.content += b'=' * (4 - missing_padding)
        
        self.content = b64decode(self.content)

    def Fill(self, data: bytes, size: int):
        self.content = data

    def Free(self):
        self.content = b''

    def __str__(self):
        return f'chunk: ... size: {self.size}'


class FileSender:

    def __init__(self, fn, chunked = False) -> None:
        
        self.chunked = chunked
        self.PathObject = Path(fn)
        self.fn = self.PathObject.name
        self.size = stat(self.PathObject).st_size

    def send(self, sock, callback):
        with open(self.PathObject, "rb") as fp:
            sock.send(fp.read())
            callback()

    def LogInformation(self, Logger):
        Logger.inform(f"File Name: {self.fn}.")
        Logger.inform(f"Size: {self.size}.")
        Logger.inform(f"Abs path: {self.PathObject}.")
    
    def GetFileHeader(self) -> dict:
        
        Rem    = self.size % CHUNK_SIZE
        
        HEADER = {
            'size': 0, # Chunk size
            'amount': (self.size - Rem) / CHUNK_SIZE
, # Chunk count
            'rem': 0  # remaining chunk size
        }
        
        
        with open(self.PathObject, 'rb') as f:
            # Just in case the cursor is off.
            f.seek(0)
            
            chunk = f.read(CHUNK_SIZE)
            HEADER['size'] = GetChunkSizeAfterEncoded(chunk)
            
            f.seek(0)
            if Rem > 0:
                f.seek(self.size - Rem) # we subntract the chunk size because we already made it off by that chunk in the beginning.
                chunk = f.read(Rem)
                HEADER['rem'] = GetChunkSizeAfterEncoded(chunk)
            
        return HEADER


    def sendChunks(self, chunkCapture: callable, progressCallback: callable):
        print()

        read = 0
        rem = (self.size % CHUNK_SIZE)
        progressCallback(self.size, read)
  
        with open(self.PathObject, "rb") as fp:         
            # Send all chunks.
            while read < self.size - rem:
                chunk = fp.read(CHUNK_SIZE)
                # prepare the chunk.
                chunkObject = Chunk(chunk)
                chunkObject.EncodeB64()
  
                # send back to the caller.
                chunkCapture(chunkObject)
     
                read += CHUNK_SIZE
                #display progress.
                progressCallback(self.size, read)
    
            if rem > 0:    
                chunk = fp.read(rem)
                 
                chunkObject = Chunk(chunk)
                chunkObject.EncodeB64()
                chunkCapture(chunkObject)

                read += rem
            
            #display progress.
            progressCallback(self.size, read)
    
    def FileInformationHeader(self, pwd) -> dict:
        if self.chunked:
            return {
                "fn": self.fn,
                "length": self.size,
                "pwd": pwd,
                "buf": 1
            }

        return {
            "fn": self.fn,
            "length": self.size,
            "pwd": pwd
        }

class FileReceiver:
    
    def __init__(self, fn=None, size=0) -> None:    
        self.fn = fn
        self.size = size
        self.Buffer = b''
    
    def SetProperties(self, fn: str, size: int):
        self.SetFn(fn)
        self.SetSize(size)

    def SetFn(self, new: str) -> str:
        self.fn = new.replace("./", "").replace(".\\", "")
        return new

    def SetSize(self, new: int) -> int: 
        self.size = new
        return new

    def writeBuff(self, out_path):
        with open(self.make_path(out_path), "wb") as fp: 
            fp.write(self.Buffer)
            self.Buffer = b''

    def DecodeReceivedBuff(self): 
        self.Buffer = b64decode(self.Buffer)

    def Notify(self, Client_, Logger):

        Logger.inform(f"Upcoming File write from : { Client_.Addr }")
        Logger.inform(f"File Name : { self.fn }")
        Logger.inform(f"size : { self.size }")
        

    def ReceiveFileBuff(self, Client_, output_path, callback, Logger):
        self.Notify(Client_, Logger)
        self.Buffer = Client_.Conn.recv(self.size)
        
        if self.Buffer and self.fn:        
            Logger.inform("Saving the file :3")
            self.writeBuff(output_path)
            Logger.success("saved!")

        callback()

    def ReceiveFileBuffChunked(self, Client_, output_path, callback, progressCallback, Logger, header):

        self.Notify(Client_, Logger)
        received = 0       
        progressCallback(self.size, received)
        
        result = (
            lambda c : Client_.Conn.send(str(c).encode(FORMAT))
        )
        
        o = self.make_path(output_path) 
        progressCallback(self.size, received)

        with open(o, 'wb') as fp:    
            while header.amount > 0:
                chunk = Client_.Conn.recv(int(header.size)) 
                chunkObj = Chunk(chunk)
                chunkObj.DecodeB64()
                
                # write the chunk.
                fp.write(chunkObj.content)

                received += header.size
                header.amount -= 1

                # Next Chunk.
                result(OK)
                progressCallback(self.size, received)
    
            if header.rem:
                chunk = Client_.Conn.recv(int(header.rem))
               
                chunkObj = Chunk(chunk)
                chunkObj.DecodeB64()
                
                # write the chunk.
                fp.write(chunkObj.content)

                received += header.rem
                # Next Chunk.
                result(OK)
            
            progressCallback(self.size, received)

            
    
        Logger.inform("Saving the file :3")
        Logger.success("saved!")

        callback()

    def make_path(self, out_dir):
        delim = "/"
        out_dir = out_dir.replace("\\", delim)
        return delim.join([out_dir, self.fn])
