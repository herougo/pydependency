import parso

RECURSIVE_GLOBAL_IGNORE = [
    parso.python.tree.Function,
    parso.python.tree.Class,
    parso.python.tree.WhileStmt,
    parso.python.tree.WithStmt,
    parso.python.tree.ForStmt,
    parso.python.tree.IfStmt
    parso.python.tree.Lambda,
    parso.python.tree.String,
    parso.python.tree.TryStmt,
    parso.python.tree.YieldExpr,
    parso.python.tree.GlobalStmt,
    parso.python.tree.Keyword,
    parso.python.tree.KeywordStatement,
    parso.python.tree.AssertStmt
]

IMPORTS = [
    parso.python.tree.Import,
    parso.python.tree.ImportFrom,
    parso.python.tree.ImportName
]

NODE_TYPES = [
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
    parso.python.tree.Scope,
]

class ParseTreeWrapper:
    def __init__(self, file_path, version='3.6'):
        self._file_path = file_path
        with open(file_path) as f:
            code = str(f.read())
        self._tree = parso.parse(code, version=version)

    @classmethod
    def _recursive_iter_nodes(cls, node, look_for, ignore):
        if hasattr(node, 'children'):
            for n2 in node.children:
                if not isinstance(n2, ignore):
                    ParseTreeWrapper._recursive_iter_nodes(n2, look_for, ignore)
        else:
            if isinstance(node, look_for):
                yield node
    
    def iter_global_class_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, parso.python.tree.Class, RECURSIVE_GLOBAL_IGNORE):
            yield node.name.value, node.start_pos, node.end_pos

    def iter_global_func_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, parso.python.tree.Function, RECURSIVE_GLOBAL_IGNORE):
            yield node.name.value, node.start_pos, node.end_pos

    def iter_global_var_names(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, parso.python.tree.Name, RECURSIVE_GLOBAL_IGNORE):
            yield node.name.value, node.start_pos, node.end_pos

    def iter_global_import(self):
        for node in ParseTreeWrapper._recursive_iter_nodes(self._tree, IMPORTS, RECURSIVE_GLOBAL_IGNORE):
            yield 0


