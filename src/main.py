import socket
from threading import Thread
from sys import argv
from Server import server
from Client import Client
from Config import RFUConfig
import datetime
from random import randint
# stripping the name of the program.
from time import sleep

PORT_FLAG, HOST_FLAG, FILE_FLAG, CHUNKED_FLAG, KEY_FLAG = '-p', '--host', '-f', '--chunked', '--key'
argv = argv[1:]
argc = len(argv)



def parseArgs(argv: list[str], argc: int) -> dict:
	
	mappedArgs = {  }
	availableArgs = [PORT_FLAG, HOST_FLAG, FILE_FLAG, KEY_FLAG]

	if argc > 0:	
		for (i, v) in enumerate(argv):
			if v in availableArgs:
				next_ = (i + 1)
				if  next_ <= (argc - 1): mappedArgs[v] = argv[next_]

	return mappedArgs


SERVER: str = "-s"
CLIENT: str = "-c"

def Settings(InstanceClass: server | Client, arg: dict):
	if HOST_FLAG in arg:
		InstanceClass.SetHost(arg[HOST_FLAG])
	
	if PORT_FLAG in arg:
		InstanceClass.SetPort(int(arg[PORT_FLAG]))

	if KEY_FLAG in arg:
		InstanceClass.SetPassword(arg[KEY_FLAG])

def ServerRoute(arg):
	s = server()
	# Takes care of auth and managing paths.
	s.SetConfigInstance(RFUConfig())
	Settings(s, arg)
	s.Listen()


def ClientRoute(arg):
	c = Client()
	Settings(c, arg)
	c.setPassword()
	c.connect()
	
	if FILE_FLAG in arg:
		
		c.SendFile(arg[FILE_FLAG], chunked_flag=(CHUNKED_FLAG in argv))
	else:
		print("File was not specified:")
		print("How to: ")
		print("-f <File relative/Abs path>")

	c.close()
	
progs = {
	"-s": ServerRoute,
	"-c": ClientRoute
}

def main():

	arguments = parseArgs(argv[1:], argc - 1)
	# print(arguments)

	if argc > 0:
		if argv[0] in progs: 
			progs[argv[0]](arguments)
	else:		
		print()
		print("Remote share command line app.")
		print("USAGE: main.py [-s/-c] -p [default: 4000] --host [default: current Host] -f <filePath> --chunked")
		print("-f used only by the client to send data.")
		print("--chunked for breaking down larger files.")

if __name__ == '__main__': 
	main()