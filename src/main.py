import socket
from threading import Thread
from sys import argv
from server import FileServer
from client import FileClient
import datetime
from random import randint
# stripping the name of the program.
from time import sleep
from Util import (
	PORT_FLAG,
	HOST_FLAG,
	FILE_FLAG,
	CHUNKED_FLAG,
	KEY_FLAG,
	RESET_FLAG,
	CLOSE,
	parseArgs
)

argv = argv[1:]
argc = len(argv)

def Settings(InstanceClass: FileServer | FileClient, arg: dict):
	if HOST_FLAG in arg:   InstanceClass.SetHost(arg[HOST_FLAG])
	if PORT_FLAG in arg:   InstanceClass.SetPort(int(arg[PORT_FLAG]))
	if KEY_FLAG in arg:    InstanceClass.SetPassword(arg[KEY_FLAG])

def FileServerRoute(arg):
	s = FileServer()
	Settings(s, arg)
	s.Listen()

def FileClientRoute(arg):
	c = FileClient()
	Settings(c, arg)
	c.setPassword()
	c.connect()
	print(arg)
	if FILE_FLAG in arg:
		fhandle = FileSender(arg[FILE_FLAG], chunked=(CHUNKED_FLAG in argv))
		c.SendFile(fhandle)
	
	if CLOSE in argv: 
		c.SendCloseServerCommand()
	
	else:
		print("File was not specified:")
		print("How to: ")
		print("-f <File relative/Abs path>")

	c.close()
	
routes = {
	"-s": FileServerRoute,
	"-c": FileClientRoute
}

def main():

	arguments = parseArgs(argv[1:], argc - 1)

	if argc > 0:
		if argv[0] in routes: 
			routes[argv[0]](arguments)
	else:		
		print()
		print("Remote share command line app.")
		print("USAGE: main.py [-s/-c] -p [default: 4000] --host [default: current Host] -f <filePath> --chunked")
		print("-f used only by the client to send data.")
		print("--chunked for breaking down larger files.")

if __name__ == '__main__': main()