import parso

RECURSIVE_GLOBAL_IMPORT_IGNORE = (
    parso.python.tree.Function,
    parso.python.tree.Class,
    parso.python.tree.WhileStmt,
    parso.python.tree.WithStmt,
    parso.python.tree.ForStmt,
    parso.python.tree.Lambda,
    parso.python.tree.String,
    parso.python.tree.TryStmt,
    parso.python.tree.YieldExpr,
    parso.python.tree.GlobalStmt,
    parso.python.tree.Keyword,
    parso.python.tree.KeywordStatement,
    parso.python.tree.AssertStmt,
    parso.python.tree.ImportFrom,
    parso.python.tree.ImportName
)

RECURSIVE_GLOBAL_IGNORE = RECURSIVE_GLOBAL_IMPORT_IGNORE + (parso.python.tree.IfStmt,)

IMPORTS = (
    parso.python.tree.Import,
    parso.python.tree.ImportFrom,
    parso.python.tree.ImportName
)

NODE_TYPES = (
    parso.python.tree.Import,
    parso.python.tree.ImportFrom,
    parso.python.tree.ImportName,
    parso.python.tree.Function,
    parso.python.tree.Class,
    parso.python.tree.Name,
    
    parso.python.tree.AssertStmt,
    parso.python.tree.BaseNode,
    parso.python.tree.ClassOrFunc,
    parso.python.tree.CompFor,
    parso.python.tree.Decorator,
    parso.python.tree.DocstringMixin,
    parso.python.tree.EndMarker,
    parso.python.tree.ErrorLeaf,
    parso.python.tree.ErrorNode,
    parso.python.tree.ExprStmt,
    parso.python.tree.FStringEnd,
    parso.python.tree.FStringStart,
    parso.python.tree.FStringString,
    parso.python.tree.Flow,
    parso.python.tree.Keyword,
    parso.python.tree.KeywordStatement,
    parso.python.tree.Leaf,
    parso.python.tree.Literal,
    parso.python.tree.Module,
    parso.python.tree.Newline,
    parso.python.tree.Node,
    parso.python.tree.Number,
    parso.python.tree.Operator,
    parso.python.tree.Param,
    parso.python.tree.PythonBaseNode,
    parso.python.tree.PythonErrorLeaf,
    parso.python.tree.PythonErrorNode,
    parso.python.tree.PythonLeaf,
    parso.python.tree.PythonMixin,
    parso.python.tree.PythonNode,
    parso.python.tree.ReturnStmt,
    parso.python.tree.Scope
)


#PYTHON_SPACING = ' ' * 4
MAX_LINE_LEN = 100

'''
if isinstance(node, parso.python.tree.ImportFrom):
    names = [n.value for n in node.get_defined_names()]
    dotted_name_node = node.children[1]
    import_location = dotted_name_node.get_code()
    yield (import_location, names, node.start_pos, node.end_pos)
elif isinstance(node, parso.python.tree.ImportName):
    # names = node.get_defined_names() # fails for import a.b
    dotted_name_node = node.children[1]
    import_location = dotted_name_node.get_code()
    #start_pos = dotted_name_node.start_pos
    #end_pos = dotted_name_node.end_pos
    yield (import_location, node.start_pos, node.end_pos)
'''

class NodeWrapper:
    name = None
    start_pos = None
    end_pos = None

    @classmethod
    def fix_pos(cls, pos):
        r, c = pos
        return r - 1, c

    @classmethod
    def from_parso_node(cls, node):
        result = NodeWrapper()
        result.name = node.name.value
        result.start_pos = NodeWrapper.fix_pos(node.start_pos)
        result.end_pos = NodeWrapper.fix_pos(node.end_pos)
        result.type = node.type


class ImportWrapper(NodeWrapper):
    @classmethod
    def from_str(cls, original_code_string):
        return ImportWrapper.from_parso_node(parso.parse(original_code_string), original_code_string)

    @classmethod
    def from_parso_node(cls, node, original_code_string=None):
        start_pos = NodeWrapper.fix_pos(node.start_pos)
        end_pos = NodeWrapper.fix_pos(node.end_pos)
        if isinstance(node, parso.python.tree.ImportFrom):
            names = [n.value for n in node.get_defined_names()]
            dotted_name_node = node.children[1]
            import_location = dotted_name_node.get_code()
            return RelativeImportWrapper(import_location, names, original_code_string, start_pos, end_pos)
        elif isinstance(node, parso.python.tree.ImportName):
            dotted_name_node = node.children[1]
            import_location = dotted_name_node.get_code()
            return AbsoluteImportWrapper(import_location, original_code_string, start_pos, end_pos)
        else:
            raise NotImplementedError()

    def __str__(self):
        raise NotImplementedError()


class AbsoluteImportWrapper(ImportWrapper):
    def __init__(self, import_location, original_code_string, start_pos, end_pos):
        self._import_location = import_location
        self._original_code_string = original_code_string
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __str__(self):
        return 'import {}'.format(self._import_location)


class RelativeImportWrapper(ImportWrapper):
    def __init__(self, import_location, names, original_code_string, start_pos, end_pos):
        self._import_location = import_location
        self._names = names
        self._original_code_string = original_code_string
        self.start_pos = start_pos
        self.end_pos = end_pos

    def __str__(self):
        # ??? Comment
        # ??? Replicate existing format
        expected_prefix_len = len(self._import_location) + 13
        expected_normal_suffix_len = sum([len(name) for name in self._names]) + 2 * (len(self._names) - 1)
        if expected_prefix_len + expected_normal_suffix_len <= MAX_LINE_LEN:
            return 'import {} from {}'.format(self._import_location, ','.join(self._names))
        first_line_with_one_name_len = expected_prefix_len + len(self._names[0]) + 1

        if expected_prefix_len / MAX_LINE_LEN >= 0.75 or first_line_with_one_name_len > MAX_LINE_LEN:
            # new line after '('
            whitespace_prefix = PYTHON_SPACING
        else:
            # line up next lines below '('
            whitespace_prefix = ' ' * (expected_prefix_len + 1)

        lines = ['from {} import ('.format(self._import_location)]
        current_line_names = []
        current_line_len = len(whitespace_prefix)
        i = 0
        while i < len(self._names):
            if len(whitespace_prefix) + len(self._names[i]) > MAX_LINE_LEN:
                raise ValueError('Big import name: {}'.format(self._names[i]))
            is_not_last = i != len(self._names) - 1
            if current_line_len + len(self._names[i] + 2 + is_not_last) > MAX_LINE_LEN:
                lines.append('{}{},'.format(whitespace_prefix, ', '.join(current_line_names)))
                current_line_names = [self._names[i]]
                current_line_len = len(whitespace_prefix) + len(self._names[i])
            else:
                assert (not is_not_last) or current_line_len != MAX_LINE_LEN
                current_line_names.append(self._names[i])
                current_line_len += 2 + len(self._names[i])
            i += 1
        assert len(current_line_names) > 0
        assert current_line_len <= MAX_LINE_LEN
        if current_line_len == MAX_LINE_LEN:
            lines.append('{}{}'.format(whitespace_prefix, ', '.join(current_line_names)))
            lines.append(')')
        else:
            lines.append('{}{})'.format(whitespace_prefix, ', '.join(current_line_names)))

        return '\n'.join(lines)

    def add_name(self, name):
        if name in self._names:
            raise ValueError('Name {} already exists in {}'.format(name, self._names))
        self._names.append(name)


class ParseTreeWrapper:
    def __init__(self, file_path, version='3.6'):
        self._file_path = file_path
        with open(file_path) as f:
            code = str(f.read())
        self._tree = parso.parse(code, version=version)

    @classmethod
    def _recursive_iter_nodes(cls, node, look_for, ignore, depth=0):
        # print('_recursive_iter_nodes', depth, type(node), isinstance(node, look_for))
        if hasattr(node, 'children'):
            for n2 in node.children:
                if isinstance(n2, look_for):
                    yield n2
                if not isinstance(n2, ignore):
                    for node2 in ParseTreeWrapper._recursive_iter_nodes(n2, look_for, ignore, depth=depth+1):
                        yield node2

    @classmethod
    def _extend_dotted_name_right(cls, node):
        result = [node]
        sibling = node
        while True:  # has attributes
            sibling = sibling.get_next_sibling()

            if not (isinstance(sibling, parso.python.tree.PythonNode) and sibling.type == 'trailer'):
                break

            n0 = sibling.children[0]
            n1 = sibling.children[1]
            if (isinstance(n0, parso.python.tree.Operator) and n0.value == '.' and
                isinstance(n1, parso.python.tree.Name)):
                result.append(n1)

        return result
    
    def iter_global_class_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, parso.python.tree.Class, RECURSIVE_GLOBAL_IGNORE):
            yield NodeWrapper.from_parso_node(node)

    def iter_global_func_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, parso.python.tree.Function, RECURSIVE_GLOBAL_IGNORE):
            yield {'name': node.name.value, 'start_pos': node.start_pos, 'end_pos': node.end_pos}

    def iter_global_var_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, parso.python.tree.Name, RECURSIVE_GLOBAL_IGNORE):
            yield {'name': node.name.value, 'start_pos': node.start_pos, 'end_pos': node.end_pos}

    def iter_global_import(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, IMPORTS, RECURSIVE_GLOBAL_IGNORE):
            for child in node.children:
                assert not (isinstance(child, parso.python.tree.Operator) and child.value == ',')  # e.g. import os, sys

            yield ImportWrapper.from_parso_node(node)
