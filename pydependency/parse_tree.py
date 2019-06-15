import parso

RECURSIVE_GLOBAL_IGNORE = (
    parso.python.tree.Function,
    parso.python.tree.Class,
    parso.python.tree.WhileStmt,
    parso.python.tree.WithStmt,
    parso.python.tree.ForStmt,
    parso.python.tree.IfStmt,
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
            yield node.name.value, node.start_pos, node.end_pos

    def iter_global_func_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, parso.python.tree.Function, RECURSIVE_GLOBAL_IGNORE):
            yield node.name.value, node.start_pos, node.end_pos

    def iter_global_var_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, parso.python.tree.Name, RECURSIVE_GLOBAL_IGNORE):
            yield node.value, node.start_pos, node.end_pos

    def iter_global_import(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, IMPORTS, RECURSIVE_GLOBAL_IGNORE):
            for child in node.children:
                assert not (isinstance(child, parso.python.tree.Operator) and child.value == ',')  # e.g. import os, sys

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
            else:
                raise NotImplementedError()


