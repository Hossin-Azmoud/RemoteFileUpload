

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
