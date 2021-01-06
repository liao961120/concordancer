from copy import deepcopy
from tabulate import tabulate
from typing import Union, Sequence, Generator

class KWIC:
    def __init__(self, concordance:Union[Sequence, Generator], print_idx:Sequence[int]=range(10)):
        self.data = concordance
        self.print_keys = ['left', 'keyword', 'right', 'captureGroups']
        self.captureGroup_keys = set()
        self.print_idx = print_idx

        self.print(print_idx=self.print_idx)
    
    def __str__(self):
        return self.data
    
    def print(self, attrs=['word', 'pos'], print_idx:Sequence[int]=None):
        """Pretty print a concordance list

        Parameters
        ----------
        attrs : list, optional
            The attributes of a token to include in printing, 
            by default ['word', 'pos']
        print_idx : Sequence[int], optional
            Indicies of the instances of the concordance list 
            to print out, by default None. If None, all instances 
            are printed out.
        """
        print_data = []
        for concord in self.data:
            concord = _keep_dict_keys(concord, self.print_keys)

            if 'captureGroups' in concord:
                for label, tokens in concord.get('captureGroups').items():
                    label = f"LABEL: {label}"
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
        
        if print_idx != None:
            print_data2 = []
            for i in print_idx:
                try:
                    x = print_data[i]
                except:
                    continue
                print_data2.append(x)
            print_data = print_data2
        
        print(tabulate(print_data, headers="keys"))


    def _separate_attrs(self, concord: dict, attrs: list):
        """Paste multiple attributes of a token together for printing

        Parameters
        ----------
        concord : dict
            A concordance object
        attrs : list
            Names of attributes to paste together

        Returns
        -------
        dict
            An concordance object with lists replaced with string 
            for printing
        """

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
