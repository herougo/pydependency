b = []
def get_used_names(t):
    names = []
    def recursive_step(n):
        if hasattr(n, 'children'):
            ignore = set()
            # ignore import statements
            if any([isinstance(n2, parso.python.tree.Keyword) and n2.value == 'import' for n2 in n.children]):
                return
            
            
            '''
            for j in range(len(n.children)):
                n2 = n.children[j]
                if isinstance(n2, parso.python.tree.Keyword) and (n2.value == 'def' or n2.value == 'class'):
                    ignore.add(j)
                    print(n.children)
            '''
            # ignore function/class definitions
            if isinstance(n, parso.python.tree.Class) and n.type == 'classdef':
                ignore.add(0)
                ignore.add(1)
                
            if isinstance(n, parso.python.tree.Function) and n.type == 'funcdef':
                ignore.add(0)
                ignore.add(1)
                
            # ignore function parameters
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
                
                prev_sibling = n.get_previous_sibling()

                # ignore attributes
                if isinstance(prev_sibling, parso.python.tree.Operator) and prev_sibling.value == '.':
                    return
                
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
            
                if n.value == 'bell':
                    b.append(n)
                            
                            
                names.append(('.'.join(name_parts), n.start_pos, end_pos))
    return names

if __name__ == '__main__':
    names = get_used_names(t)
    s = jedi.api.Interpreter(CODE, [{}])
    lines = CODE.split('\n')
    for name, start_pos, end_pos in names:
        s._pos = start_pos
        completions = [c._name.string_name for c in s.completions()]
        if name.split('.')[0] not in completions:
            print '***', name, start_pos, end_pos
            print '\n'.join(lines[start_pos[0] - 3: start_pos[0] + 3])



