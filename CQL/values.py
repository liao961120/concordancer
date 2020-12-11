from dataclasses import dataclass

@dataclass
class QueryTerm:
    value: dict

    def __repr__(self):
        return str(self.value)
