![Support Python Version](https://img.shields.io/badge/python-%E2%89%A5%203.7-blue.svg)

# Concordancer

This module loads and indexes a corpus in RAM and provides concordance search to retrieve data from the corpus using (a subset of) Corpus Query Language (CQL).


## Installation

```bash
pip install -U concordancer
```


## Usage

### Loading a corpus from file

```python
import json
from concordancer.demo import download_demo_corpus
from concordancer.concordancer import Concordancer
from concordancer import server

# Load demo corpus
fp = download_demo_corpus(to="~/Desktop")
with open(fp, encoding="utf-8") as f:
    corpus = [ json.loads(l) for l in f ]

# Index and initiate the corpus as a concordancer object
C = Concordancer(corpus)
C.set_cql_parameters(default_attr="word", max_quant=3)
```

### Interactive Search Interface

You can start an interactive server to query and read results through your browser:

```python
server.run(C)
```


### CQL Concordance search

```python
cql = '''
verb:[pos="V.*"] noun:[pos="N[abch]"]
'''
concord_list = C.cql_search(cql, left=2, right=2)
```

The result of the concordance search is a generator, which can be converted to a list of dictionaries (and then to JSON or other data structures for further uses):

```python
>>> concord_list = list(concord_list)
>>> concord_list[:2]
[
    {
        'left': [{'word': '買', 'pos': 'VC'}, {'word': '了', 'pos': 'Di'}],
        'keyword': [{'word': '覺得', 'pos': 'VK'}, {'word': '材質', 'pos': 'Na'}],
        'right': [{'word': '很', 'pos': 'Dfa'}, {'word': '對', 'pos': 'VH'}],
        'position': {'doc_idx': 78, 'sent_idx': 13, 'tk_idx': 9},
        'captureGroups': {'verb': [{'word': '覺得', 'pos': 'VK'}],
                          'noun': [{'word': '材質', 'pos': 'Na'}]}
    },
    {
        'left': [{'word': '“', 'pos': 'PARENTHESISCATEGORY'},
                 {'word': '不', 'pos': 'D'}],
        'keyword': [{'word': '戴', 'pos': 'VC'}, {'word': '錶', 'pos': 'Na'}],
        'right': [{'word': '世代', 'pos': 'Na'}, {'word': '”', 'pos': 'VC'}],
        'position': {'doc_idx': 52, 'sent_idx': 7, 'tk_idx': 36},
        'captureGroups': {'verb': [{'word': '戴', 'pos': 'VC'}],
                          'noun': [{'word': '錶', 'pos': 'Na'}]}
    }
]
```


### Keyword in Context

To better read the concordance lines, pass `concord_list` into `concordancer.kwic_print.KWIC()` to print them as a keyword-in-context format in the console:

```python
>>> from concordancer.kwic_print import KWIC
>>> KWIC(concord_list[:5])
left                        keyword          right             LABEL: verb    LABEL: noun
--------------------------  ---------------  ----------------  -------------  -------------
買/VC 了/Di                 覺得/VK 材質/Na  很/Dfa 對/VH      覺得/VK        材質/Na
“/PARENTHESISCATEGORY 不/D  戴/VC 錶/Na      世代/Na ”/VC      戴/VC          錶/Na
聯名鞋/Na 趁著/P            過年/VA 期間/Na  穿出去/VB 四處/D  過年/VA        期間/Na
走/VA  /WHITESPACE          燒/VC 錢/Na      啊/T ～/FW        燒/VC          錢/Na
正/VH 韓/Nc                 賣/VD 家/Nc      裡面/Ncd 很/Dfa   賣/VD          家/Nc
```


This will open a query interface where you can interact with the corpus.


## Supported CQL features

CQL search is supported through [`cqls`](https://github.com/liao961120/cqls), in which a (quite useful) subset of CQL is implemented:

- token: `[]`, `"我"`, `[word="我"]`, `[word!="我" & pos="N.*"]`
- token-level quantifier: `+`, `*`, `?`, `{n,m}`
- grouping: `("a" "b"? "c"){1,2}`
- label: `lab1:[word="我" & pos="N.*"] lab2:("a" "b")`
