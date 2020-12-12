from nodes import *
from values import QueryTerm

# def print(x=None):
#     pp.pprint(x)

class Interpreter:
    def __init__(self, default_attrname: str, quantifier_max: int=10):
        self.default_attrname = default_attrname
        self.quantifier_max = quantifier_max
    
    def visit(self, node):
        # AttrNameNode => visit_AttrNameNode
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name)
        return method(node)
        # return flatten_2dim(method(node))
    
    def visit_list(self, node):
        out = []
        for n in node:
            if isinstance(n, list):
                n = self.visit_list(n)
            else:
                n = self.visit(n)
                if (not isinstance(n, list)) and (not isinstance(n, dict)):
                    n = n.value
            out.append(n)
        
        return out

    def visit_AssignAttrNode(self, node):
        qt = {
            'match': {},
            'not_match': {}
        }

        attr_name = f"{node.node_a.value}"
        attr_value = f"{node.node_b.value}"

        if node.operator == 'is':
            qt['match'][attr_name] = [ attr_value ]
        elif node.operator == 'is_not':
            qt['not_match'][attr_name] = [ attr_value ]
        
        return QueryTerm(qt)

    def visit_DefaultTokenNode(self, node):
        return QueryTerm({
            'match': {
                f"{self.default_attrname}": [ f"{node.value}" ]
            },
            'not_match': {}
        })

    def visit_EmptyTokenNode(self, node):
        return QueryTerm({})

    def visit_ConjoinAttrNode(self, node):
        qt = conjoin_dict(self.visit(node.node_a).value, self.visit(node.node_b).value)
        return QueryTerm(qt)
    
    def visit_QuantifyNode(self, node):
        """[summary]

        Parameters
        ----------
        node : [type]
            [description]

        Returns
        -------
        """
        min_, max_ = node.quantifier

        if isinstance(node.node_a, list):
            queryTerms = []
            for n in node.node_a:
                visited = self.visit(n)
                if isinstance(visited, list):
                    queryTerms.append(visited)
                else:
                    queryTerms.append(visited.value)
        else:
            visited = self.visit(node.node_a)
            if isinstance(visited, list):
                queryTerms = [ visited ]
            else:
                queryTerms = [ visited.value ]
        
        # Enemerate all possible kinds of queries
        lst_of_queryTerms = []
        for i in range(min_, max_ + 1):
            lst_of_queryTerms.append( queryTerms * i )
        
        return lst_of_queryTerms


    def visit_LabelNode(self, node):
        label = node.label
        qts = []

        if isinstance(node.node_a, list):
            for n in node.node_a:
                n = self.visit(n)
                if not isinstance(n, list):
                    n = n.value
                qts.append(n)
        else:
            qts = self.visit(node.node_a)
            if not isinstance(qts, list):
                qts = qts.value

        return add_label(qts, label)

## ToDo: flatten final (QT tagged with labels, if given) output data     


#%%
def flatten_nested_queries_to_2dim(lst: list):
    """[summary]

    Parameters
    ----------
    lst : list
        [description]

    Miniumum nested structure:
    []

    [{}, {}]
    
    [
        [{}, {}, {}],
        [{}, {}, {}]
    ]
    
    [
        [
            [{}, {}, {}],
            [{}, {}, {}]
        ]
    ]
    """
    # Check structure
    struct = ''
    lev1_nested, lev2_nested  = 0, 0
    for elem_l1 in lst:
        if isinstance(elem_l1, list):
            lev1_nested += 1
        for elem_l2 in elem_l1:
            if isinstance(elem_l2, list):
                lev2_nested += 1
    if lev1_nested == len(lst):
        nested_level = 2
    if lev2_nested == ''
        pass

    # Deal with 3 or more nested structure


def unnest_one_level(lst: list):
    return lst[0]

def is_nested(lst: list):
    for elem in lst:
        if isinstance(elem, list):
            return True
    return False

def conjoin_dict(dict1, dict2):
    qt = {
        'match': {},
        'not_match': {}
    }

    # Add two dicts together
    for operator in qt:
        for d_ in [dict1, dict2]:
            for attr_name, attr_values in d_[operator].items():
                if attr_name not in qt[operator]:
                    qt[operator][attr_name] = set()
                for val in attr_values:
                    qt[operator][attr_name].add(val)
    
    # Remove duplicate values
    for operator in qt:
        for attr_name in qt[operator]:
            qt[operator][attr_name] = list(qt[operator][attr_name])
    
    return qt

def add_label(qts, label):
    if isinstance(qts, dict):
        return add_label_qt(qts, label)
    
    # Recursively add label to nested query terms
    if isinstance(qts, list):
        out = []
        for elem in qts:
            if isinstance(elem, dict):
                qt = add_label_qt(elem, label)
            elif isinstance(elem, list):
                qt = add_label(elem, label)
            else:
                print('=====Error in add_label()========')
                print(elem)
                print('=================================')
                raise Exception("None qt found")
            
            out.append(qt)
    
        return out

def add_label_qt(qt, label):
    if '__label__' not in qt:
        qt['__label__'] = []
    if label not in qt['__label__']:
        qt['__label__'].append(label)
    return qt




# %%
d1 = {
    'match': {
        'a': [ 'aaa' ]
    },
    'not_match': {}
}

d2 = {
    'match': {
        'a': [ 'aaa' ]
    },
    'not_match': {
        'b': [ 'bbb', 'bbbb', 'cccc']
    }
}

#conjoin_dict(d1, d2)
# %%
"""
base_case: "a"{0,2}
[
    [],
    ["a"],
    ["a", "a"]
]

nested_group: ("a"{0,2} "b"){1,2} "c"
[
    ["b"{1,2}, "c"],
    [("a" "b"){1,2}, "c"],
    [("a", "a", "b"){1,2}, "c"],
]

[
    [
        ["b"],
        ["a", "b"],
        ["a", "a", "b"],
    ],
    [
        ["b", "b"],
        ["a", "b", "a", "b"],
        ["a", "a", "b", "a", "a", "b"],
    ],
]

"""