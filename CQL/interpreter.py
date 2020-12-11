from nodes import *
from values import QueryTerm
from copy import deepcopy

class Interpreter:
    def __init__(self, default_attrname: str, quantifier_max: int=10):
        self.default_attrname = default_attrname
        self.quantifier_max = quantifier_max
    
    def visit(self, node):
        # AttrNameNode => visit_AttrNameNode
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name)
        return method(node)

    def visit_AssignAttrNode(self, node):
        qt = {
            'match': {},
            'not_match': {}
        }

        attr_name = f"{self.visit(node.node_a).value}"
        attr_value = f"{self.visit(node.node_b).value}"

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
        list
            [
                [ {<qt>}, {<qt>}, {<qt>}, ... ],  # query 1
                [ {<qt>}, {<qt>}, {<qt>}, ... ],  # query 2
                ...
            ]
        """
        min_, max_ = node.quantifier

        if isinstance(node.node_a, list):
            queryTerms = [ self.visit(x).value for x in node.node_a ]
        else:
            queryTerms = [ self.visit(node.node_a).value ]
        
        # Enemerate all possible kinds of queries
        lst_of_queryTerms = []
        for i in range(min_, max_ + 1):
            lst_of_queryTerms.append( queryTerms * i )
        
        ### DEBUG: Recursion function for expanding nested list ######
        
        return lst_of_queryTerms

    def visit_LabelNode(self, node):
        qt = conjoin_dict(self.visit(node.node_a).value, self.visit(node.node_b).value)
        return QueryTerm(qt)
        


#%%
def expand_nested_quantifiers(lst_of_queryTerms: list):
    out = []

    for qts in lst_of_queryTerms:
        while is_nested(qts):
            qts = expand_nested_quantifiers(qts)
        out.append(qts)
    
    return out

def is_nested(lst: list):
    for x in lst:
        if isinstance(x, list):
            return True
    return False      

def unest_one_level(lst: list):
    out = []
    for elem_lev1 in lst:
        for elem_lev2 in elem_lev1:
            out.append(elem_lev2)
    return out

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
