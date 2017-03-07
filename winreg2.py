import os
import sys


if sys.version_info[0] == 2:
	import _winreg as win
else:
	import winreg as win

STANDARD_KEYS = {
	'HKLM': win.HKEY_LOCAL_MACHINE,
	'HKEY_LOCAL_MACHINE': win.HKEY_LOCAL_MACHINE,
}
	

class RegistryKey():
	""" Wrapper for winreg Key objects. """

	def __init__(self, name):
		self.name = name
		
	@property
	def contains_values(self):
		return win.QueryInfoKey(self.key)[1] > 0

	def __getitem__(self, item):
		return win.QueryValueEx(self.key, item)[0]
	
	def get(self, item, default_value):
		value = None
		try:
			value = self.__getitem__(item)
		except FileNotFoundError as e:
			value = default_value
		return value
	
	def _get_registry_values(self):
		_, value_count, _ = win.QueryInfoKey(self.key)
		for index in range(value_count):
			yield win.EnumValue(self.key, index)
	
	def keys(self):
		return map(lambda v: v[0], self._get_registry_values())
		
	def values(self):
		return map(lambda v: v[1], self._get_registry_values())
	
	def items(self):
		return map(lambda v: (v[0], v[1]), self._get_registry_values())
	
	def walk(self):
		""" Recursively traverses all sub-keys in tree. """
		key_count, _, _ = win.QueryInfoKey(self.key)
		yield self
		for index in range(key_count):
			child = self.__class__(self.name + "\\" + win.EnumKey(self.key, index))
			with child as c:
				yield from c.walk()
	
	def __enter__(self):
		key_code, key_path = self.name.split(':')
		self.key = win.OpenKey(STANDARD_KEYS[key_code], key_path)
		return self
		
	def __exit__(self, type_, value, traceback):
		win.CloseKey(self.key)
		if type_:
			type_(value)
