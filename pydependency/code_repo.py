import collections

PYTHON_SPACING = ' ' * 4
MAX_LINE_LEN = 100

class Import:
	@classmethod
	def from_str(cls, string):
		raise NotImplementedError()
		
	def __str__(self):
		raise NotImplementedError()

		
class AbsoluteImport(Import):
	
	@classmethod
	def from_str(cls, string):
		raise NotImplementedError()
		
	def __str__(self):
		return f'import {self.package}'
	
class RelativeImport(Import):
	
	@classmethod
	def from_str(cls, string):
		raise NotImplementedError()
		
	def __str__(self):
		expected_prefix_len = len(self.package) + 13
		expected_normal_suffix_len = sum([len(x) for name in self.names]) + 2 * (len(self.names) - 1)
		
		if expected_prefix_len + expected_normal_suffix_len <= MAX_LINE_LEN:
			return f'import {self.package} from {','.join(self.names)}'
		elif expected_prefix_len / MAX_LINE_LEN >= 0.75:
			NotImplementedError()


class CodeFile:
	def __init__(self, file_path):
		self._file_path = file_path
		self._tree = ParseTree(file_path)

	def iter_class_names(self):
		# iter_classdefs
		self._iter_names('iter_class_names')
		
	def iter_function_names(self):
		# iter_funcdefs
		self._iter_names('iter_function_names')
		
	def iter_global_var_names(self):
		self._iter_names('iter_global_var_names')
	
	def iter_imports(self):
		# iter_imports

class CodeRepo:
	def __init__(self, config_folder, folder_path=None):
		if folder_path is None:
			self._config = load_json_if_exists(os.path.join(config_folder, 'config.json'))
			self._folder_path = self._config['folder_path']
		else:
			self._folder_path = folder_path
		#self._code_files = [CodeFile(file_path) for file_path in file_paths]
		# keys are folder_names and leaf values are CodeFile objects
		self._dict_thing = self._build_dict_thing()
		self._relative_import_map = self._build_relative_import_map()
		
		

	def _get_python_file_paths_old(self):
		result = []
		for paths, subdirs, files in os.walk(self._folder_path):
			for file in files:
				if file.endswith('.py'):
					pure_path = os.path.join(paths, file)
					result.append(pure_path)
		return result

	def _build_dict_thing(self):
		result = {}
		
		def _build_dict_thing_recursion(folder_path, d):
			for f in os.listdir(folder_path):
				path = os.path.join(folder_path, f):
				if os.path.isdir(path):
					dir_name = os.path.basename(path)
					if os.path.isfile(os.path.join(path, '__init__.py')):
						d[dir_name] = {}
						self._build_dict_thing(self, path, d[dir_name])
				elif os.path.isfile(path) and path.endswith('.py'):
					file_name = os.path.basename(path)
					d[file_name] = CodeFile(path)
		
		_build_dict_thing_recursion(self._folder_path, result)
		
		return result
	
	def _build_relative_import_map(self):
		result = collections.defaultdict(list)
		
		def _build_map_recursion(prefix_list, node):
			if isinstance(node, dict):
				for k, v in top1.items():
					_iter_names_recursion(prefix_list + [k], v)
			else:
				if prefix_list[-1] == '__init__.py':
					prefix = '.'.join(prefix_list[:-1])
				else:
					prefix = '.'.join(prefix_list)
				for name in node.iter_names():
					_self._relative_import_map[name].append(prefix)
		
		_build_map_recursion([], result)
		
		return result
				
	def _iter_names(self, func_name):
		def _iter_names_recursion(prefix_list, node):
			if isinstance(node, dict):
				for k, v in top1.items():
					_iter_names_recursion(prefix_list + [k], v)
			else:
				if prefix_list[-1] == '__init__.py':
					prefix = '.'.join(prefix_list[:-1])
				else:
					prefix = '.'.join(prefix_list)
				for name in getattr(node, func_name)():
					yield f'{prefix}.{name}'
		self._iter_names_recursion([], self._dict_thing)
	
	def iter_class_names(self):
		# iter_classdefs
		self._iter_names('iter_class_names')
		
	def iter_function_names(self):
		# iter_funcdefs
		self._iter_names('iter_function_names')
		
	def iter_global_var_names(self):
		self._iter_names('iter_global_var_names')
	
	def iter_imports(self):
		# iter_imports
		
	def get_relative_import_dependencies(self, name):
		'''
		Input: name of a directory or name in the repo_path
		Output: relative import statements from the repo which can load this name
		Example: 'path' -> ['from os import path']
		'''
		self._relative_import_map[name]
		
	def transform_import_star(self, import_str):
		# ????
		pass