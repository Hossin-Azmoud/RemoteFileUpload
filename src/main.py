import socket
from threading import Thread
from sys import argv
from Server import server
from Client import Client

argv = argv[1:]
argc = len(argv)
SERVER: str = "-s"
CLIENT: str = "-c"

def ServerRoute():
	s = server()
	s.Listen()

def ClientRoute():
	c = Client()
	c.SetHost(argv[1])
	c.setPassword()
	c.connect()
	c.SendFile(argv[2])
	c.close()
	
progs = {
	"-s": ServerRoute,
	"-c": ClientRoute
}

def main():
	if argc > 0:
		if argv[0] in progs: progs[argv[0]]()



if __name__ == '__main__': 
	main()