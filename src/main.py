import socket
from threading import Thread
from sys import argv
from server import FileProtocolServer
from client import FileProtocolClient
import datetime
from random import randint
# stripping the name of the program.
from time import sleep
from FileHandler import FileSender

from Util import (
	Help,
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

def Settings(InstanceClass: FileProtocolServer | FileProtocolClient, arg: dict):
	if HOST_FLAG in arg:   InstanceClass.SetHost(arg[HOST_FLAG])
	if PORT_FLAG in arg:   InstanceClass.SetPort(int(arg[PORT_FLAG]))
	if KEY_FLAG in arg:    InstanceClass.SetPassword(arg[KEY_FLAG])

def FileServerRoute(arg):
	""" Listen for file protocol client requests. """
	s = FileProtocolServer()
	Settings(s, arg)
	s.Listen()

def FileClientRoute(arg):
	""" send requests to file protocol server requests. """
	
	c = FileProtocolClient()
	check = False
	Settings(c, arg)
	c.setPassword()
	c.connect()

	if FILE_FLAG in arg:
		# Send fil. arg[FILE_FLAG] is a path to the file.s.
		fhandle = FileSender(arg[FILE_FLAG], chunked=(CHUNKED_FLAG in argv))
		c.SendFile(fhandle)
		check = True

	if CLOSE in argv: 
		c.SendCloseServerCommand()
		check = True

	if not check: Help()
	
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
		Help()

if __name__ == '__main__': main()