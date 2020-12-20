# Concordancer

This module loads and indexes a corpus in RAM and provides concordance search to retrieve data from the corpus using (a subset of) Corpus Query Language (CQL).


## Installation

```bash
pip install concordaner
```


## Usage

### Loading a corpus from file

```python
import json
from concordancer.concordancer import Concordancer
from concordancer.kwic_print import KWIC

# Read corpus from file
corpus = []
with open("test-data/tokenDict.jsonl") as f:
    for l in f:
        corpus.append(json.loads(l))

# Index and initiate the corpus as a concordance object
C = Concordancer(corpus)
C.set_cql_parameters(default_attr="word", max_quant=3)
```

### CQL Concordance search

```python
cql = '''
[pos="V.*"]+
'''
concord_list = C.cql_search(cql, left=2, right=2)
```

The result of the concordance search is a list of dictionaries, which can easily be converted to JSON or other data structures for further uses:

```python
>>> concord_list[:2]
[
    {
        'left': [{'word': '來', 'pos': 'VA'}, {'word': '一', 'pos': 'Neu'}],
        'keyword': [{'word': '小', 'pos': 'VH'}, {'word': '段', 'pos': 'Nf'}],
        'right': [{'word': '故事', 'pos': 'Na'},
                  {'word': '。', 'pos': 'PERIODCATEGORY'}],
        'position': {'doc_idx': 16, 'sent_idx': 3, 'tk_idx': 21},
        'captureGroups': {'verb': [{'word': '小', 'pos': 'VH'}],
                          'noun': [{'word': '段', 'pos': 'Nf'}]}
    },
    {
        'left': [{'word': '長度', 'pos': 'Na'}, {'word': '剛好', 'pos': 'Da'}],
        'keyword': [{'word': '蓋住', 'pos': 'VC'}, {'word': '這', 'pos': 'Nep'}],
        'right': [{'word': '件', 'pos': 'Nf'}, {'word': '裙子', 'pos': 'Na'}],
        'position': {'doc_idx': 78, 'sent_idx': 59, 'tk_idx': 4},
        'captureGroups': {'verb': [{'word': '蓋住', 'pos': 'VC'}],
                          'noun': [{'word': '這', 'pos': 'Nep'}]}
    }
]
```

To better read the concordance lines, you can pass `concord_list` into `concordancer.kwic_print.KWIC()` to read them as keyword-in-context format in the console:

```python
>>> KWIC(concord_list[:5])
left             keyword                         right                      LABEL: verb    LABEL: noun
---------------  ------------------------------  -------------------------  -------------  ----------------------
來/VA 一/Neu     小/VH 段/Nf                     故事/Na 。/PERIODCATEGORY  小/VH          段/Nf
長度/Na 剛好/Da  蓋住/VC 這/Nep                  件/Nf 裙子/Na              蓋住/VC        這/Nep
復古/VH 帥氣/VH  穿搭/VA ！/EXCLAMATIONCATEGORY  <URL>/FW 身高/Na           穿搭/VA        ！/EXCLAMATIONCATEGORY
長/VH 的話/Cba   有/V_2 什麼/Nep                 解決/VC 的/DE              有/V_2         什麼/Nep
買/VC 了/Di      覺得/VK 材質/Na                 很/Dfa 對/VH               覺得/VK        材質/Na
```


## Supported CQL features

CQL search is supported through [`cqls`](https://github.com/liao961120/cqls). A subset of useful CQL is supported:

- token: `[]`, `"我"`, `[word="我"]`, `[word!="我" & pos="N.*"]`
- token-level quantifier: `+`, `*`, `?`, `{n,m}`
- grouping: `("a" "b"? "c"){1,2}`
- label: `lab1:[word="我" & pos="N.*"] lab2:("a" "b")`