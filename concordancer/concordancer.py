import re
import math
import cqls
from typing import Union
from copy import deepcopy
from collections import Counter
from .utils import queryMatchToken, match_mode
from .indexedCorpus import IndexedCorpus


class Concordancer(IndexedCorpus):

    _cql_default_attr = "word"
    _cql_max_quantity = 6

    def cql_search(self, cql: str, left=5, right=5):
        """Search the corpus with Corpus Query Language

        Parameters
        ----------
        cql : str
            A CQL query
        left : int, optional
            Left context size, by default 5
        right : int, optional
            Right context size, by default 5

        Yields
        -------
        dict
            A dictionary with the structure:

            .. code-block:: python

                {
                    'left': [<tk>, <tk>, ...],
                    'keyword': [<tk>, <tk>, ...],
                    'right': [<tk>, <tk>, ...],
                    'position': {
                        'doc_idx': <int>, 
                        'sent_idx': <int>, 
                        'tk_idx': <int>
                    },
                    'captureGroups': {
                        'verb': [<tk>],
                        'noun': [<tk>]}
                }
            
            where ``<tk>`` is a token, represented as a dictionary,
            for instance: 

            .. code-block:: python

                {
                    'word': 'hits', 
                    'lemma': 'hit',
                    'pos': 'V',
                }
        """
        queries = cqls.parse(cql, default_attr=self._cql_default_attr,max_quant=self._cql_max_quantity)

        for query in queries:
            for result in self._kwic(keywords=query, left=left, right=right):
                yield result


    def set_cql_parameters(self, default_attr: str, max_quant: int=6):
        """Set parameters for CQL queries in the Concordancer

        Parameters
        ----------
        default_attr : str
            The default attribute of the tokens. CQL allows expressing
            a token without specifying its attribute, like ``"hits"``. 
            If ``default_attr`` is set to, for example, ``word``, 
            ``"hits"`` is then equivalent to ``[word="hits"]`` in CQL.
        max_quant : int, optional
            The maximium quantity to evaluate to for the CQL token-level
            quantifier. ``max_quant`` is used in two CQL expressions: ``+``
            and ``*``. The upper bounds of these quantifiers are theoretically
            infinite, but since the computer cannot generate a infinite number
            of queries, an upper bound of the quantifier must be specified. 
            By default, it is set to 6.
        """
        self._cql_default_attr = default_attr
        self._cql_max_quantity = max_quant


    def _kwic(self, keywords: list, left=5, right=5):
        # Get concordance from corpus
        search_results = self._search_keywords(keywords)
        if search_results is None: 
            return []
        for doc_idx, sent_idx, tk_idx in search_results:
            cc = self._kwic_single(doc_idx, sent_idx, tk_idx, tk_len=len(keywords), left=left, right=right, keywords=keywords)
            yield cc
        
        
    def _kwic_single(self, doc_idx, sent_idx, tk_idx, tk_len=1, left=5, right=5, keywords:list=None):
        # Flatten doc sentences to a list of tokens
        text, keyword_idx = flatten_doc_to_sent(self._get_corp_data(doc_idx))

        tk_start_idx = keyword_idx(sent_idx, tk_idx)
        tk_end_idx = tk_start_idx + tk_len
        start_idx = max(tk_start_idx - left, 0)
        end_idx = min(tk_end_idx + right, len(text))

        # Get CQL labeled token positions
        captureGroups = {}
        for i, keyword in enumerate(keywords):
            if '__label__' in keyword:
                for lab in keyword.get('__label__'):
                    if lab not in captureGroups:
                        captureGroups[lab] = []
                    tk = self._get_corp_data(doc_idx, sent_idx, i + tk_idx)
                    captureGroups[lab].append(tk)

        return {
            "left": text[start_idx:tk_start_idx],
            "keyword": text[tk_start_idx:tk_end_idx],
            "right": text[tk_end_idx:end_idx],
            "position": {
                "doc_idx": doc_idx,
                "sent_idx": sent_idx,
                "tk_idx": tk_idx
            },
            "captureGroups": captureGroups
        }


    def _search_keywords(self, keywords: list):
        #########################################################
        # Find keywords with the least number of matching results 
        #########################################################
        best_search_loc = (0, None, math.inf)
        for i, keyword in enumerate(keywords):
            results = self._search_keyword(keyword)
            num_of_matched = len(results)
            if num_of_matched == 0: 
                return None
            elif num_of_matched < best_search_loc[-1]:
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
                if queryMatchToken(queryTerm=w_k, corpToken=w_c):
                    matched_num += 1
            if matched_num == len(keywords):
                first_keyword_idx = idx[2] - keyword_anchor['seed_idx']
                matched_results.append( [idx[0], idx[1], first_keyword_idx] )
            
        return matched_results


    def _search_keyword(self, keyword: dict):
        """Global search of a keyword to find candidates of correct kwic instances

        Parameters
        ----------
        keyword : dict
            A dictionary specifying the matching conditions of
            the keyword:

            .. code-block:: python
            
                {
                    'match': {
                        'word': ['打'],
                        'pos': ['V.*']
                    }, 
                    'not_match': {
                        'pos': ['VH.*']
                    },
                    '__label__': ['l1']  #labels to attached to search results  
                }

        Returns
        -------
        list
            A list of matching indicies
        """
        positive_match = set()
        negative_match = set()

        # Deal with empty token {}
        if ('match' not in keyword) and ('not_match' not in keyword):
            return self.all_tk_idx

        else:
            ########################################
            ##########   POSITIVE MATCH   ##########
            ########################################
            matching_idicies = Counter()
            for tag, values in keyword['match'].items():
                # Check all values of a specific tag
                for idx in self._intersect_search(tag, values):
                    matching_idicies.update({idx: 1})
            
            # Get indicies that matched all given tags 
            for idx, count in matching_idicies.items():
                if count == len(keyword['match']):
                    positive_match.add(idx)
            
            # Special case: match is empty
            if len(keyword['match']) == 0:
                positive_match = self.all_tk_idx
            
            ########################################
            ##########   NEGATIVE MATCH   ##########
            ########################################
            for tag, values in keyword['not_match'].items():
                for idx in self._union_search(tag, values):
                    negative_match.add(idx)

            ########################################
            #####  POSITIVE - NEGATIVE MATCH  ######
            ########################################
            positive_match.difference_update(negative_match)

        if len(positive_match) == 0:
            print(f"{keyword} not found in corpus")

        return positive_match


    def _union_search(self, tag:Union[str, int], values:list):
        """Given candidates values, return from corpus the position 
        of tokens matching any of the values

        Parameters
        ----------
        tag : Union[str, int]
            The tag of the token used for comparison
        values : list
            A list of values to compare with
        """
        matched_indicies = set()

        for value in values:
            value, mode = match_mode(value)
            if mode == "literal":
                if value in self.corp_idx[tag]:
                    for idx in self.corp_idx[tag][value]: 
                        matched_indicies.add(idx)
            else:
                for term in self.corp_idx[tag]:
                    if re.search(value, term):
                        for idx in self.corp_idx[tag][term]:
                            matched_indicies.add(idx)
        
        return matched_indicies


    def _intersect_search(self, tag:Union[str, int], values:list):
        """Given candidates values, return from corpus the position 
        of tokens matching all values

        Parameters
        ----------
        tag : Union[str, int]
            The tag of the token used for comparison
        values : list
            A list of values to compare with
        """
        # Get intersections of all values
        match_count = Counter()
        for value in values:
            value, mode = match_mode(value)
            indices = []
            if mode == "literal":
                if value in self.corp_idx[tag]:
                    indices = self.corp_idx[tag][value]
            else:
                for term in self.corp_idx[tag]:
                    if re.search(value, term):
                        indices += self.corp_idx[tag][term]
            
            for idx in set(indices):
                match_count.update({idx: 1})
        
        # Filter idicies that match all values given
        intersect_match = set()
        for idx, count in match_count.items():
            if count == len(values):
                intersect_match.add(idx)
        
        return intersect_match
        


    def _get_keywords(self, search_anchor: dict, doc_idx, sent_idx, tk_idx):
        sent = self._get_corp_data(doc_idx, sent_idx)
        start_idx = max(0, tk_idx - search_anchor['seed_idx'])
        end_idx = min(start_idx + search_anchor['length'], len(sent))
        
        return sent[start_idx:end_idx]


    def _get_corp_data(self, doc_idx, sent_idx=None, tk_idx=None):
        """Get corpus data by position
        """
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
