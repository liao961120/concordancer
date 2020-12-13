from dataclasses import dataclass

@dataclass
class AttrNameNode:
    value: str

    def __repr__(self):
        return f"{self.value}"

@dataclass
class AttrValueNode:
    value: str

    def __repr__(self):
        return f"{self.value}"

@dataclass
class AssignAttrNode:
    node_a: any
    operator: any
    node_b: any

    def __repr__(self):
        return f"({self.node_a} {self.operator} {self.node_b})"

@dataclass
class DefaultTokenNode:
    value: any

    def __repr__(self):
        return f"(DFTattr is {self.value})"

@dataclass
class EmptyTokenNode:
    def __repr__(self):
        return "EMPTY_TOKEN"

@dataclass
class ConjoinAttrNode:
    node_a: any
    node_b: any

    def __repr__(self):
        return f"({self.node_a} & {self.node_b})"

@dataclass
class QuantifyNode:
    node_a: any
    quantifier: int

    def __repr__(self):
        return f"{self.node_a}" + "{" + f"{self.quantifier}" "}"

@dataclass
class LabelNode:
    node_a: any
    label: any

    def __repr__(self):
        return f"{self.label}:{self.node_a}"
