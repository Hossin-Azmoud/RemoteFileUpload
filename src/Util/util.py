

PORT_FLAG = '-p'
HOST_FLAG = '--host'
FILE_FLAG = '-f'
CHUNKED_FLAG = '--chunked'
KEY_FLAG = '--key'
RESET_FLAG = '--reset'
CLOSE = '--shutdown'

SERVER: str = "-s"
CLIENT: str = "-c"

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
