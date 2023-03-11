"""
AVAILABLE COLORS FOR THE INTERFACE:
	BLACK
	BLUE
	CYAN
	GREEN
	LIGHTBLACK_EX
	LIGHTBLUE_EX
	LIGHTCYAN_EX
	LIGHTGREEN_EX
	LIGHTMAGENTA_EX
	LIGHTRED_EX
	LIGHTWHITE_EX
	LIGHTYELLOW_EX
	MAGENTA
	RED
	RESET
	WHITE
	YELLOW
"""

from colorama import Fore as Colors
from colorama import Back as BColors
from sys import stdout
from datetime import datetime
from Transmission import GetSizeInProperUnit

PROGRESS_BAR_BACKGROUND = BColors.YELLOW
RESET_BACKGROUND = BColors.RESET
RESET = Colors.RESET

PORT_FLAG = '-p'
HOST_FLAG = '--host'
FILE_FLAG = '-f'
CHUNKED_FLAG = '--chunked'
KEY_FLAG = '--key'
RESET_FLAG = '--reset'
CLOSE = '--shutdown'

SERVER: str = "-s"
CLIENT: str = "-c"

DEFAULT_TEXT_COLOR = Colors.LIGHTYELLOW_EX

INFO 	= f"{Colors.LIGHTYELLOW_EX}[+] "
ERROR 	= f"{Colors.RED}[!] "
SUCCESS = f"{Colors.GREEN}[*] "
DELETE 	= f"{Colors.YELLOW}[-] "

__FLAGS = [PORT_FLAG, HOST_FLAG, FILE_FLAG, CHUNKED_FLAG, KEY_FLAG]

def parseArgs(argv: list[str], argc: int) -> dict:
	
	mappedArgs = {  }
		
	if argc > 0:	
		for (i, v) in enumerate(argv):
			if v in __FLAGS:
				next_ = (i + 1)
				if  next_ <= (argc - 1): mappedArgs[v] = argv[next_]

	return mappedArgs

def Help():
	print()
	print("Remote share command line app.")
	print("USAGE: main.py [-s/-c] -p [default: 4000] --host [default: current Host] -f <filePath> --chunked")
	print("-f used only by the client to send data.")
	print("--chunked for breaking down larger files.")



class Logger:
	# TODO: Implement the logger to make colored and dated text.
	def __init__(self, File=None):
		if File: 
			self.logFile = File

	@property
	def CurrentTime(self): return datetime.now()
	
	def Log(self, T: str, ctx: str) -> None: stdout.write(f"{ctx} <{self.CurrentTime}> {T}{RESET}\n")
	
	def error(self, T: str="<err>") -> None: self.Log(T, ERROR)
	
	def success(self, T: str="<success>") -> None:  self.Log(T, SUCCESS)
	
	def inform(self, T: str="<info>") -> None: self.Log(T, INFO)

	def logDeletion(self, T: str="<deletion>") -> None: self.Log(T, DELETE)
		

def progressBar(All, Proccessed, c=' '):
	# TODO Implement a general prog bar for client/server or sender/receiver.
	e = '\r'
	all__ = 100
	current = ((Proccessed * all__) / All)

	if int(current//1) == 100: e = '\n\n'

	stdout.write(f"{ PROGRESS_BAR_BACKGROUND }{ c * int(current  // 2) } {RESET_BACKGROUND} { int(current//1) }%/100% | all: { GetSizeInProperUnit(int( All//1 )) }{e}")
	stdout.write(f"{ RESET_BACKGROUND }")
