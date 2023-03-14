from sys import argv
from Util import (
	Help,
	parseArgs
) 
  
from __init__ import ROUTES, argv
argc = len(argv)

def main():

	arguments = parseArgs(argv[1:], argc - 1)
	
	if argc > 0:
		if argv[0] in ROUTES:
			ROUTES[argv[0]](arguments)
	else: 
		Help()

if __name__ == '__main__':
	main()