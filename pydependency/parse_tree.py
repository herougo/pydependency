import parso
import jedi
import warnings
from pydependency.config import PYTHON_VERSION, MAX_LINE_LEN, PYTHON_SPACING

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

NODE_WRAPPER_SUPPORTED = (
    parso.python.tree.Function,
    parso.python.tree.Class,
    parso.python.tree.Name
)


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

def get_parso_nodes_right_of(nodes: list, right_of_predicate):
    for j in range(len(nodes)):
        if right_of_predicate(nodes[j]):
            return nodes[j + 1:]
    return []

def is_as_operator(node):
    return isinstance(node, parso.python.tree.Keyword) and node.value == 'as'

class NodeWrapper:
    name = None
    start_pos = None
    end_pos = None

    @classmethod
    def fix_pos(cls, pos):
        # parso pos line numbers start at 1 and NodeWrapper starts at 0
        r, c = pos
        return r - 1, c

    @classmethod
    def unfix_pos(cls, pos):
        r, c = pos
        return r + 1, c

    @classmethod
    def from_parso_node(cls, node):
        if not isinstance(node, NODE_WRAPPER_SUPPORTED):
            raise NotImplementedError()
        result = NodeWrapper()
        result.name = node.value if isinstance(node, parso.python.tree.Name) else node.name.value
        result.start_pos = NodeWrapper.fix_pos(node.start_pos)
        result.end_pos = NodeWrapper.fix_pos(node.end_pos)
        result.type = node.type
        return result


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
            if isinstance(dotted_name_node, parso.python.tree.PythonNode) and dotted_name_node.type == 'dotted_as_name':
                as_name_nodes = get_parso_nodes_right_of(dotted_name_node.children, is_as_operator)
                assert len(as_name_nodes) == 1, (node, as_name_nodes)
                import_location = dotted_name_node.children[0].get_code()
                as_name = as_name_nodes[0].value
            else:
                import_location = dotted_name_node.get_code()
                as_name = None
            return AbsoluteImportWrapper(import_location, original_code_string, start_pos, end_pos, as_name=as_name)
        else:
            raise NotImplementedError()

    @classmethod
    def merge(cls, list_of_imports):
        absolute_import_location_set = set()
        relative_import_location_map = {}
        result = []
        for imp in list_of_imports:
            if isinstance(imp, AbsoluteImportWrapper):
                if imp.import_location not in absolute_import_location_set:
                    result.append(imp)
            else:
                if imp.import_location in relative_import_location_map.keys():
                    existing_imp = relative_import_location_map[imp.import_location]
                    for name in imp.names:
                        existing_imp.add_name(name)
                else:
                    relative_import_location_map[imp.import_location] = imp
                    result.append(imp)
        return result


    def __str__(self):
        raise NotImplementedError()


class AbsoluteImportWrapper(ImportWrapper):
    def __init__(self, import_location, original_code_string=None, start_pos=None, end_pos=None, as_name=None):
        self._import_location = import_location
        self._as_name = as_name
        self._original_code_string = original_code_string
        self.start_pos = start_pos
        self.end_pos = end_pos

    @property
    def import_location(self):
        return self._import_location

    @property
    def as_name(self):
        return self._as_name

    @property
    def used_name(self):
        return self._as_name if self._as_name is not None else self._import_location

    def __str__(self):
        suffix = '' if self._as_name is None else ' as {}'.format(self._as_name)
        return 'import {}{}'.format(self._import_location, suffix)


class RelativeImportWrapper(ImportWrapper):
    # REFACTOR: handle as
    def __init__(self, import_location, names, original_code_string=None, start_pos=None, end_pos=None):
        self._import_location = import_location
        self._names = names
        self._original_code_string = original_code_string
        self.start_pos = start_pos
        self.end_pos = end_pos

    @property
    def names(self):
        return self._names

    @property
    def import_location(self):
        return self._import_location

    def __str__(self):
        # ??? Handle Comments
        # ??? Replicate existing format (ie spacing)
        expected_prefix_len = len(self._import_location) + 13
        expected_normal_suffix_len = sum([len(name) for name in self._names]) + 2 * (len(self._names) - 1)
        if expected_prefix_len + expected_normal_suffix_len <= MAX_LINE_LEN:
            return 'from {} import {}'.format(self._import_location, ','.join(self._names))
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
            return
        self._names.append(name)


class ParseTreeWrapper:
    def __init__(self, file_path, version=PYTHON_VERSION, need_unused_names=True):
        self._file_path = file_path
        with open(file_path) as f:
            code = str(f.read())
        if need_unused_names:
            self._jedi_interpreter = jedi.api.Interpreter(code, [{}])
            self._tree = self._jedi_interpreter._module_node
        else:  # lightweight version
            self._jedi_interpreter = None
            self._tree = parso.parse(code, version=version)

    @classmethod
    def _recursive_iter_nodes(cls, node, predicate_fn, ignore, depth=0):
        # print('_recursive_iter_nodes', depth, type(node), isinstance(node, look_for))
        if hasattr(node, 'children'):
            for n2 in node.children:
                if predicate_fn(n2):
                    yield n2
                if not isinstance(n2, ignore):
                    for node2 in ParseTreeWrapper._recursive_iter_nodes(n2, predicate_fn, ignore, depth=depth+1):
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
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, ParseTreeWrapper.is_class_node, RECURSIVE_GLOBAL_IGNORE):
            yield NodeWrapper.from_parso_node(node)

    def iter_global_func_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, ParseTreeWrapper.is_func_node, RECURSIVE_GLOBAL_IGNORE):
            yield NodeWrapper.from_parso_node(node)

    def iter_global_var_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, ParseTreeWrapper.is_name_node, RECURSIVE_GLOBAL_IGNORE):
            yield NodeWrapper.from_parso_node(node)

    def iter_global_import(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, ParseTreeWrapper.is_import_node, RECURSIVE_GLOBAL_IGNORE):
            for child in node.children:
                assert not (isinstance(child, parso.python.tree.Operator) and child.value == ',')  # e.g. import os, sys

            yield ImportWrapper.from_parso_node(node)

    def get_used_names(self):
        # REFACTOR: Keep output consistent with NodeWrapper?
        warnings.warn('This code is experimental')
        names = []

        def recursive_step(n):
            if hasattr(n, 'children'):
                ignore = set()
                # ignore import statements
                if any([isinstance(n2, parso.python.tree.Keyword) and n2.value == 'import' for n2 in n.children]):
                    return

                # ignore function/class definitions
                if isinstance(n, parso.python.tree.Class) and n.type == 'classdef':
                    ignore.add(0)
                    ignore.add(1)

                if isinstance(n, parso.python.tree.Function) and n.type == 'funcdef':
                    ignore.add(0)
                    ignore.add(1)

                # ignore function parameters
                # TODO: Edge case of using default parameter values
                if isinstance(n, parso.python.tree.PythonNode) and n.type == 'parameters':
                    return

                # ignore assignments
                i = 0
                while i < len(n.children):
                    if isinstance(n.children[i], parso.python.tree.Operator) and n.children[i].value == '=':
                        break
                    i += 1
                if i >= len(n.children):
                    i = 0

                # otherwise
                for j in range(i, len(n.children)):
                    if j not in ignore:
                        recursive_step(n.children[j])
            else:
                if isinstance(n, parso.python.tree.Name):
                    # ignore attributes
                    prev_sibling = n.get_previous_sibling()
                    if isinstance(prev_sibling, parso.python.tree.Operator) and prev_sibling.value == '.':
                        return

                    # get full dotted name
                    sibling = n
                    name_parts = [n.value]
                    end_pos = n.end_pos
                    while True:  # has attributes
                        sibling = sibling.get_next_sibling()

                        if not (isinstance(sibling, parso.python.tree.PythonNode) and sibling.type == 'trailer'):
                            break

                        n0 = sibling.children[0]
                        n1 = sibling.children[1]
                        if (isinstance(n0, parso.python.tree.Operator) and n0.value == '.' and
                                isinstance(n1, parso.python.tree.Name)):
                            name_parts.extend([n1.value])
                            end_pos = n1.end_pos

                    names.append(('.'.join(name_parts), NodeWrapper.fix_pos(n.start_pos), NodeWrapper.fix_pos(end_pos)))

        recursive_step(self._tree)

        return names

    def get_undefined_used_names(self):
        # REFACTOR: Keep output consistent with NodeWrapper?
        assert self._jedi_interpreter is not None
        result = []

        names = self.get_used_names()
        for name, start_pos, end_pos in names:
            self._jedi_interpreter._pos = NodeWrapper.unfix_pos(start_pos)
            completions = [c._name.string_name for c in self._jedi_interpreter.completions()]
            if name.split('.')[0] not in completions:
                result.append((name, NodeWrapper.fix_pos(start_pos), NodeWrapper.fix_pos(end_pos)))

        return result

    @classmethod
    def is_class_node(cls, node):
        return isinstance(node, parso.python.tree.Class)

    @classmethod
    def is_func_node(cls, node):
        return isinstance(node, parso.python.tree.Function) and node.type == 'funcdef'

    @classmethod
    def is_name_node(cls, node):
        return isinstance(node, parso.python.tree.Name)

    @classmethod
    def is_import_node(cls, node):
        return isinstance(node, IMPORTS)