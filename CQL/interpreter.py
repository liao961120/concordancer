from nodes import *
from values import QueryTerm
from itertools import chain


class Interpreter:
    def __init__(self, default_attrname: str):
        self.default_attrname = default_attrname
    
    def visit(self, node):
        # AttrNameNode => visit_AttrNameNode
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name)
        result = method(node)
        if isinstance(result, list):
            result = flatten_list(result)
        return result
    
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
        quant_num = node.quantifier

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
                queryTerms = visited
            else:
                queryTerms = [ visited.value ]

        # Expand quantifier
        queryTerms =  queryTerms * quant_num        
        return queryTerms


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
                qts = [ qts.value ]
        
        # Flatten data
        qts = flatten_list(qts)

        return add_label(qts, label)


################################
####### Helper functions #######
################################
def flatten_list(lst: list):
    out = []
    for elem in lst:
        if not isinstance(elem, list):
            out.append(elem)
        else:
            flatten = flatten_list(elem)
            out += flatten
    
    return out

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
    if isinstance(qts, list):
        return [ add_label_qt(qt, label) for qt in qts ]
    raise Exception(f"Unexpected data struct: {qts}")


def add_label_qt(qt, label):
    if '__label__' not in qt:
        qt['__label__'] = []
    if label not in qt['__label__']:
        qt['__label__'].append(label)
    return qt
