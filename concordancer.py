#%%
import re
import math
from typing import Union
from copy import deepcopy
from collections import Counter


class Concordancer():

    def __init__(self, corpus: list, text_key="text"):
        """[summary]

        Parameters
        ----------
        corpus : list
            Corpus data

        Notes
        -----
        Structure of corpus could be:
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
                        
                        # Update corpus structure
                        if self.text_key is not None:
                            self.corpus[doc_idx][self.text_key][sent_idx][tk_idx] = token
                        else:
                            self.corpus[doc_idx][sent_idx][tk_idx] = token

    
    def kwic(self, keywords: Union[str, list], default_tag="word", left=5, right=5, regex=False):

        if default_tag not in self.corp_idx:
            print(f"`{default_tag}` not an attribute in the corpus")
            print(f"  available attributes: {', '.join(self.corp_idx.keys())}")
            return []
        
        if isinstance(keywords, str): 
            keywords = [ {f"{default_tag}":keywords} ]

        # Get concordance from corpus
        concordance_list = []
        search_results = self._search_keywords(keywords, default_tag, regex)
        if search_results is None: 
            return search_results
        for doc_idx, sent_idx, tk_idx in search_results:
            cc = self._kwic_single(doc_idx, sent_idx, tk_idx, tk_len=len(keywords), left=left, right=right)
            concordance_list.append(cc)
        
        return concordance_list

        
    def _kwic_single(self, doc_idx, sent_idx, tk_idx, tk_len=1, left=5, right=5):
        # Flatten doc sentences to a list of tokens
        text, keyword_idx = flatten_doc_to_sent(self.get_corp_data(doc_idx))

        tk_start_idx = keyword_idx(sent_idx, tk_idx)
        tk_end_idx = tk_start_idx + tk_len
        start_idx = max(tk_start_idx - left, 0)
        end_idx = min(tk_end_idx + right, len(text))

        return {
            "left": text[start_idx:tk_start_idx],
            "keyword": text[tk_start_idx:tk_end_idx],
            "right": text[tk_end_idx:end_idx],
            "position": {
                "doc_idx": doc_idx,
                "sent_idx": sent_idx,
                "tk_idx": tk_idx
            }
        }


    def _search_keywords(self, keywords: list, default_tag="word", regex=False):
        for i, keyword in enumerate(deepcopy(keywords)):
            if isinstance(keyword, str):
                keywords[i] = { f"{default_tag}": keyword.strip() }
            else:
                if not isinstance(keyword, dict): raise Exception("keywords should be a list of str or dict")
        
        #########################################################
        # Find keywords with the least number of matching results 
        #########################################################
        best_search_loc = (0, None, math.inf)
        for i, keyword in enumerate(keywords):
            results = self._search_keyword(keyword, regex)
            if results is None: 
                return None
            num_of_matched = len(results)
            if num_of_matched < best_search_loc[-1]:
                best_search_loc = (i, results, num_of_matched)
        results = best_search_loc[1]

        #######################################
        # Check other tokens around search seed
        #######################################
        keyword_anchor = {
            'length': len(keywords),
            'seed_idx': best_search_loc[0]
        }
        
        # Check all possible matching keywords
        matched_results = []
        for idx in results:
            # Get all possible matching keywords from corpus
            candidates = self._get_keywords(keyword_anchor, *idx)
            if len(candidates) != len(keywords): 
                continue
            # Check every token in keywords
            matched_num = 0
            for w_k, w_c in zip(keywords, candidates):
                if is_subdict(w_k, w_c, regex):
                    matched_num += 1
            if matched_num == len(keywords):
                first_keyword_idx = idx[2] - keyword_anchor['seed_idx']
                matched_results.append( [idx[0], idx[1], first_keyword_idx] )
        
        return matched_results


    def _search_keyword(self, keyword: dict, regex=False):
        """Search keyword with complex conditions in the corpus

        Parameters
        ----------
        keyword : dict
            A dictionary specifying the matching conditions of
            the keyword:
                {
                    "word": "打",
                    "pos": "V"
                }
        regex : bool, optional
            Whether values in `keyword` is written in regex, 
            by default False

        Returns
        -------
        list
            A list of matching indicies
        """
        matched_indicies = []
        candidate_indicies = []
        if not regex:
            for tag, value in keyword.items():
                indicies = self.corp_idx[tag].get(value, None)
                if indicies is None:
                    break
                candidate_indicies += indicies
        else:
            for tag, value in keyword.items():
                value = re.compile(value)
                term_candidates = []
                for term in self.corp_idx[tag]:
                    if value.search(term): 
                        term_candidates += self.corp_idx[tag].get(term)
                term_candidates = list(set(term_candidates))
                candidate_indicies += term_candidates

        num_of_conditions = len(keyword)
        for idx, freq in Counter(candidate_indicies).items():
            if freq == num_of_conditions:
                matched_indicies.append(idx)
        
        if len(matched_indicies) == 0:
            print(f"{keyword} not found in corpus")
        return matched_indicies



    def _get_keywords(self, search_anchor: dict, doc_idx, sent_idx, tk_idx):
        
        sent = self.get_corp_data(doc_idx, sent_idx)
        start_idx = max(0, tk_idx - search_anchor['seed_idx'])
        end_idx = min(start_idx + search_anchor['length'], len(sent))
        
        return sent[start_idx:end_idx]


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


##################
# Helper functions
##################
def flatten_doc_to_sent(doc):
    text = []
    sent_lengths = []
    for sent in doc:
        sent_lengths.append(len(sent))
        text += sent

    def keyword_idx(sent_idx, tk_idx):
        nonlocal sent_lengths
        for i in range(sent_idx):
            tk_idx += sent_lengths[i]
        return tk_idx
    
    return text, keyword_idx
        

def norm_token_struct(token):
    if isinstance(token, dict):
        return token
    if isinstance(token, str):
        return {"word": token}
    if isinstance(token, list):
        return { i:item for i, item in enumerate(token) }
    raise Exception("Invalid token structure")


def is_subdict(subdict:dict, dict_:dict, regex=False):
    for k in subdict:
        if k not in dict_: return False
        if not regex:
            if subdict[k] != dict_[k]: return False
        else:
            if not re.search(subdict[k], dict_[k]): return False
    return True


#############
# Test
#############
if __name__ == "__main__":
    import json
    corpus = []
    with open("test-data/tokenDict.jsonl") as f:
        for l in f:
            corpus.append(json.loads(l))

    C = Concordancer(corpus)
    C.kwic("我.", regex=True)[:3]
# %%
