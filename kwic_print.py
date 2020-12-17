from copy import deepcopy
from tabulate import tabulate

class KWIC:
    def __init__(self, concordance: list):
        self.data = deepcopy(concordance)
        self.print_keys = ['left', 'keyword', 'right', 'captureGroups']
        self.captureGroup_keys = set()
    
    def __str__(self):
        return self.data
    
    def print(self, attrs=['word', 'pos']):
        print_data = []
        for concord in self.data:
            concord = _keep_dict_keys(concord, self.print_keys)

            if 'captureGroups' in concord:
                for label, tokens in concord.get('captureGroups').items():
                    label = f"label: {label}"
                    concord[label] = tokens
                    self.captureGroup_keys.add(label)
                del concord['captureGroups']

            # Add captureGroup keys to print keys
            for k in self.captureGroup_keys:
                if k not in self.print_keys:
                    self.print_keys.append(k)

            # Separate word/tag
            concord = self._separate_attrs(concord, attrs)
            print_data.append(concord)
        
        print(tabulate(print_data, headers="keys"))


    def _separate_attrs(self, concord, attrs):
        for key in self.print_keys:
            if key == 'captureGroups': continue
            tokens = []
            for token in concord[key]:
                concat_val = []
                for attr, val in token.items():
                    if attr in attrs:
                        concat_val.append(val)
                concat_val = '/'.join(concat_val)
                tokens.append(concat_val)
            concord[key] = ' '.join(tokens)
                            
        return concord


def _keep_dict_keys(dict_, keys):
    for k in deepcopy(dict_):
        if k not in keys:
            del dict_[k]
    return dict_
