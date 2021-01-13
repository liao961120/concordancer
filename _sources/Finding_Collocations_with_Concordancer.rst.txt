Finding Collocations with Concordancer
======================================

This
`notebook <https://colab.research.google.com/drive/1kTASc3fcvsia4kTCsNWr_JJ4EsrAfS-S>`__
demonstrates how one can use
`Concordancer <https://github.com/liao961120/concordancer>`__ to find
collocates of a word from the corpus.

.. code:: ipython3

    !pip install -U concordancer


.. parsed-literal::

    Requirement already up-to-date: concordancer in /usr/local/lib/python3.6/dist-packages (0.1.13)
    Requirement already satisfied, skipping upgrade: falcon-cors in /usr/local/lib/python3.6/dist-packages (from concordancer) (1.1.7)
    Requirement already satisfied, skipping upgrade: cqls in /usr/local/lib/python3.6/dist-packages (from concordancer) (0.1.5)
    Requirement already satisfied, skipping upgrade: falcon in /usr/local/lib/python3.6/dist-packages (from concordancer) (2.0.0)
    Requirement already satisfied, skipping upgrade: tabulate in /usr/local/lib/python3.6/dist-packages (from concordancer) (0.8.7)


.. code:: ipython3

    import json
    from math import log2
    from concordancer.concordancer import Concordancer
    from concordancer.kwic_print import KWIC
    
    # Use built-in example data
    from concordancer.demo import download_demo_corpus
    fp = download_demo_corpus(to=".")


.. parsed-literal::

    Corpus downloaded to /content/demo_corpus.jsonl


.. code:: ipython3

    # Load corpus as an Concordancer object
    with open(fp, encoding="utf-8") as f:
        C = Concordancer([json.loads(l) for l in f], text_key="text")
    
    C.set_cql_parameters(default_attr="word", max_quant=5)

Extracting Collocates
---------------------

-  The code below extracts collocates of the node word *討厭*
-  These collocates must occur within a window size of **4** around the
   node word to be counted
-  **MI** is used as the association measure

.. code:: ipython3

    # Count co-occurrances
    NODE_WORD = '討厭'
    WINDOW = 4
    
    cql = f'[word="{NODE_WORD}"]'
    results = C.cql_search(cql, left=WINDOW, right=WINDOW)
    
    collo_stats = {}
    for result in results:
        context_words = [ w['word'] for w in result['left'] + result['right'] ]
        for collocate in context_words:
            if collocate not in collo_stats: 
                collo_stats[collocate] = {
                    'cooccur': 0,
                    'total': len(C.corp_idx["word"][collocate]),
                }
            collo_stats[collocate]['cooccur'] += 1
    
    collo_stats




.. parsed-literal::

    {'人': {'cooccur': 1, 'total': 79},
     '外套': {'cooccur': 1, 'total': 58},
     '很': {'cooccur': 1, 'total': 244},
     '我': {'cooccur': 1, 'total': 470},
     '是': {'cooccur': 1, 'total': 450},
     '的': {'cooccur': 1, 'total': 1190},
     '真的': {'cooccur': 1, 'total': 90},
     '穿厚': {'cooccur': 1, 'total': 1}}



.. code:: ipython3

    # Compute association measures
    corpus_size = sum( len(positions) for positions in C.corp_idx['word'].values() )
    node_marginal_count = len(C.corp_idx["word"][NODE_WORD])
    
    for word, stats in collo_stats.items():
        observed_cooccur = stats['cooccur']
        collocate_marginal_count = stats['total']
    
        # Calculate MI
        expected_cooccur = collocate_marginal_count * node_marginal_count / corpus_size
        MI = log2(observed_cooccur / expected_cooccur)
        collo_stats[word]['MI'] = MI

.. code:: ipython3

    # Sort results
    sorted(collo_stats.items(), key=lambda x:x[1]['MI'], reverse=True)[:10]




.. parsed-literal::

    [('穿厚', {'MI': 14.693759179520415, 'cooccur': 1, 'total': 1}),
     ('外套', {'MI': 8.835778184392844, 'cooccur': 1, 'total': 58}),
     ('人', {'MI': 8.389978431343312, 'cooccur': 1, 'total': 79}),
     ('真的', {'MI': 8.20190608319074, 'cooccur': 1, 'total': 90}),
     ('很', {'MI': 6.763021841957529, 'cooccur': 1, 'total': 244}),
     ('是', {'MI': 5.879977988303378, 'cooccur': 1, 'total': 450}),
     ('我', {'MI': 5.817242232955415, 'cooccur': 1, 'total': 470}),
     ('的', {'MI': 4.477013321325109, 'cooccur': 1, 'total': 1190})]


