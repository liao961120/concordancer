#%%
import math
import re
from typing import Union


class Concordancer():

    def __init__(self, corpus: list, text_key="text"):
        """[summary]

        Parameters
        ----------
        corpus : list
            [
                {
                    ...,
                    "<text_dictkey>": [
                        {"word": "<word>", "pos": "<pos>"},
                        {"word": "<word>", "pos": "<pos>"},
                        {"word": "<word>", "pos": "<pos>"},
                        ...
                    ]
                }
            ]
        """
        self.corpus = corpus
        self.corp_idx = {}

        # Detect corpus structure
        a_token = corpus[0][text_key][0][0]
        token_struct = type(a_token)
        if (token_struct is not dict) and (token_struct is not list) and (token_struct is not str):
            raise Exception(f"Structure of token in text should be dict, list, or str, not {token_struct}")
        a_token = norm_token_struct(a_token)
        for tag in a_token: self.corp_idx[tag] = {}

        # Index corpus
        for doc_idx, doc in enumerate(corpus):
            for sent_idx, sent in enumerate(doc[text_key]):
                for tk_idx, token in enumerate(sent):
                    token = norm_token_struct(token)
                    for tag, item in token.items():
                        if item not in self.corp_idx[tag]:
                            self.corp_idx[tag][item] = []
                        position = (doc_idx, sent_idx, tk_idx)
                        self.corp_idx[tag][item].append(position)
                        # Update corpus structure
                        self.corpus[doc_idx][text_key][sent_idx][tk_idx] = token

    
    def kwic(self, keywords: Union[str, list], tag="word", left=5, right=5, regex=False):
        if tag not in self.corp_idx:
            print(f"`{tag}` not an attribute in the corpus")
            print(f"  available attributes: {', '.join(self.corp_idx.keys())}")
            return []
        
        if isinstance(keywords, str): keywords = [ keywords ]

        # Get concordance from corpus
        concordance_list = []
        for doc_idx, sent_idx, tk_idx in self._search_keywords(keywords, tag, regex):
            cc = self._kwic_single(doc_idx, sent_idx, tk_idx, tk_len=len(keywords), left=left, right=right)
            concordance_list.append(cc)
        
        return concordance_list

        
    def _kwic_single(self, doc_idx, sent_idx, tk_idx, tk_len=1, left=5, right=5):
        # Flatten doc sentences to a list of tokens
        text, keyword_idx = flatten_doc_to_sent(self.corpus[doc_idx])

        tk_start_idx = keyword_idx(sent_idx, tk_idx)
        tk_end_idx = tk_start_idx + tk_len
        start_idx = min(tk_start_idx - left, 0)
        end_idx = max(tk_end_idx + right, len(text))

        return {
            "left": text[start_idx:tk_idx],
            "keyword": text[tk_start_idx:tk_end_idx],
            "right": text[tk_end_idx:end_idx]
        }


    def _search_keywords(self, keywords: list, tag="word", regex=False):
        keywords = [k.strip() for k in keywords]
        
        #########################################################
        # Find keywords with the least number of matching results 
        #########################################################
        best_search_loc = (0, None, math.inf)
        for i, keyword in enumerate(keywords):
            results = self._search_keyword(keyword, tag, regex)
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
        
        if regex: keywords = [re.compile(k) for k in keywords]

        # Check all possible matching keywords
        matched_results = []
        for idx in results:
            # Get possible matching keywords from corpus
            candidates = self.get_keywords(keyword_anchor, *idx)
            if len(candidates) != len(keywords): continue
            # Check every token in keywords
            matched_num = 0
            for w_k, w_c in zip(keywords, candidates):
                if regex:
                    if not w_k.match(w_c): continue
                else:
                    if w_k != w_c: continue
                matched_num += 1
            if matched_num == len(keywords):
                first_keyword_idx = idx[2] - keyword_anchor['seed_idx']
                matched_results.append( [idx[0], idx[1], first_keyword_idx] )
        
        return matched_results


    def _search_keyword(self, keyword: str, tag="word", regex=False):
        if not regex:
            keyword_idx = self.corp_idx[tag].get(keyword, None)
            if keyword_idx is None:
                print(f"{keyword} not in corpus")
            return keyword_idx
        else:
            matched_keyword_idx = []
            keyword = re.compile(keyword.strip())
            for term in self.corp_idx[tag]:
                if keyword.match(term): 
                    matched_keyword_idx += self.corp_idx[tag][term]
            return sorted( x for x in set(matched_keyword_idx) )


    def get_keywords(self, search_anchor: dict, doc_idx, sent_idx, tk_idx):
        start_idx = min(0, tk_idx - search_anchor['seed_idx'])
        end_idx = max(start_idx + len(search_anchor['length']), len(self.corpus[doc_idx][sent_idx]))

        return self.corpus[doc_idx][sent_idx][start_idx:end_idx]


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




#############
# Test
#############
import json
corpus = []
with open("test-data/tokenDict.jsonl") as f:
    for l in f:
        corpus.append(json.loads(l))

C = Concordancer(corpus)
# %%
