import os
import sys

# Version compat
if sys.version_info[0] == 2:
	import _winreg as win
else:
	import winreg as win

HKEY_LOCAL_MACHINE = win.HKEY_LOCAL_MACHINE

class RegistryKey:
	""" Wrapper for winreg Key object with high-level methods. """
	
	def __init__(self, reg, name):
		self._reg = reg
		self.name = name
		self._attribs = {}
		
	def _init_attributes(self):
		attrib_count, _, _ = win.QueryInfoKey(self.key)
		for index in range(attrib_count):
			try:
				attr = win.EnumValue(self.key, index)
				self._attribs[attr[0]] = attr[1]
			except OSError as e:
				pass
			except:
				raise
	
	def __contains__(self, item):
		return item in self._attribs

	def __getitem__(self, item):
		return self._attribs[item]
	
	def walk(self):
		""" Recursively traverses all sub-keys in tree. """
		child_count, _, _ = win.QueryInfoKey(self.key)
		yield self
		for index in range(child_count):
			child = self.__class__(self._reg, self.name + "\\" + win.EnumKey(self.key, index))
			with child as c:
				yield from c.walk()

	def __enter__(self):
		self.key = win.OpenKey(self._reg, self.name)
		self._init_attributes()
		return self
	
	def __exit__(self, e_type, e_value, e_traceback):
		win.CloseKey(self.key)
		if e_type is not None:
			raise
