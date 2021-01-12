import re
import math
from typing import Union
from copy import deepcopy
from collections import Counter


class IndexedCorpus:

    def __init__(self, corpus: list, text_key="text"):
        """Indexing corpus

        Parameters
        ----------
        corpus : list
            Corpus data
        text_key: str
            The key to where text is stored in a JSON file,
            by default "text"

        Notes
        -----
        Structure of corpus could be:

        .. code-block:: python

            [
                {
                    "<text_dictkey>": [
                        {"word": "<word>", "pos": "<pos>"},
                        {"word": "<word>", "pos": "<pos>"},
                        {"word": "<word>", "pos": "<pos>"},
                        ...
                    ],
                    ...
                }
            ]
        
        Or, simply a nested list:

        .. code-block:: python
        
            [
                [
                    [
                        ["<word>", "<pos>"],
                        ["<word>", "<pos>"],
                        ["<word>", "<pos>"],
                        ...
                    ]
                ],
                [...],  # another text
                ...
            ]
        """
        self.corpus = corpus
        self.corp_idx = {}
        self.all_tk_idx = set()
        self.text_key = text_key

        # Detect corpus structure
        a_token = self.get_corp_data(doc_idx=0, sent_idx=0, tk_idx=0)
        token_struct = type(a_token)
        if (token_struct is not dict) and (token_struct is not list) and (token_struct is not str):
            raise Exception(f"Structure of token in text should be dict, list, or str, not {token_struct}")
        a_token = norm_token_struct(a_token)
        for tag in a_token: self.corp_idx[tag] = {}

        # Index corpus
        for doc_idx, doc in enumerate(corpus):
            if self.text_key is not None: enum = doc[text_key]
            else: enum = doc
            for sent_idx, sent in enumerate(enum):
                for tk_idx, token in enumerate(sent):
                    token = norm_token_struct(token)
                    for tag, item in token.items():
                        if item not in self.corp_idx[tag]:
                            self.corp_idx[tag][item] = []
                        position = (doc_idx, sent_idx, tk_idx)
                        self.corp_idx[tag][item].append(position)
                        self.all_tk_idx.add(position)
                        
                        # Update corpus structure
                        if self.text_key is not None:
                            self.corpus[doc_idx][self.text_key][sent_idx][tk_idx] = token
                        else:
                            self.corpus[doc_idx][sent_idx][tk_idx] = token


    def get_corp_data(self, doc_idx, sent_idx=None, tk_idx=None):
        if self.text_key is not None:
            if sent_idx is None:
                return self.corpus[doc_idx][self.text_key]
            if tk_idx is None:
                return self.corpus[doc_idx][self.text_key][sent_idx]
            return self.corpus[doc_idx][self.text_key][sent_idx][tk_idx]
        else:
            if sent_idx is None:
                return self.corpus[doc_idx]
            if tk_idx is None:
                return self.corpus[doc_idx][sent_idx]
            return self.corpus[doc_idx][sent_idx][tk_idx]


def norm_token_struct(token):
    if isinstance(token, dict):
        return token
    if isinstance(token, str):
        return {"word": token}
    if isinstance(token, list):
        return { i:item for i, item in enumerate(token) }
    raise Exception("Invalid token structure")
