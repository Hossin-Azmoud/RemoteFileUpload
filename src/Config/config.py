from json import dump, load
from os import path
from hashlib import sha256
from pprint import pprint

class RFUConfig:
	"""  """	
	
	def __init__(self):
		self.configPath = "./server_config.json"
		self.ConfigObject = {}
		
		if not (self.LoadConfig()):
			self.AddConfig()
	@property
	def SavePath(self): return self.ConfigObject["save_path"]
	def joinWithSavePath(self, o): 
		return path.join(self.SavePath, o)
	
	def GetValueByKey(self, k): return self.ConfigObject[k]
	def SetValue(self, k, v):
		self.LoadConfig()
		if (k and v): 
			self.ConfigObject[k] = v
			self.DumpConfig(self.ConfigObject)
			return True
		return False

	def HashPwd(self, pwd):
		return sha256(pwd.encode()).hexdigest()

	def AddConfig(self):
		config = {
			"pwd": self.HashPwd("1234567890"),
			"save_path": "./RFUFiles"
		}
		
		savepath = input(f'Save path (default => ./RFUFiles): ')
		if savepath.strip():
			config["save_path"] = savepath.strip()

		pwd = input(f'Server Password (default => 1234567890): ')
		if pwd.strip():
			config["pwd"] = self.HashPwd(pwd.strip())
		
		config["hash_mapping"] = f'{ pwd.strip() } -> { self.HashPwd(pwd.strip()) }'

		
		pprint(config)

		flag = input("OK? (Y/N): ")

		if flag.strip().upper() != "Y":
			self.AddConfig()
		else:
			
			self.ConfigObject = {
				"pwd": config["pwd"],
				"save_path": config["save_path"]
			}

			self.DumpConfig(self.ConfigObject)

	def LoadConfig(self):
		if path.exists(self.configPath):
			with open(self.configPath) as fp:
				self.ConfigObject = load(fp)
				return True
		return False

	def DumpConfig(self, New):
		with open(self.configPath, "w+") as f: dump(New, f)