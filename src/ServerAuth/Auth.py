# Make Loaders for password and shit.*

from hashlib import sha256
from json import dump, load
from os import path

# TODO: Make config class to load and dump config.
class Auth:	
	def __init__(self, ConfigClassInstance): self.provider = ConfigClassInstance
	def SetPassword(self, new): return self.provider.SetValue('pwd', self.GenericHash(new))
	def CheckPassword(self, P): return ( self.provider.pwd == self.GenericHash(P) )
	def GenericHash(self, s): return sha256(s.encode()).hexdigest()
	
def ConstructAuthManager(ConfigInstance) -> Auth: return Auth(ConfigInstance)