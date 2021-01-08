import os
import pathlib
import zipfile
import urllib.request

DEMO_DATA = 'https://raw.githubusercontent.com/liao961120/concordancer/main/test-data/demo_corpus.jsonl.zip'


def download_demo_corpus(to:str='.'):
    """Dowload demo corpus data

    Parameters
    ----------
    to : str, optional
        Path to the directory to save the corpus, by default '.'

    Returns
    -------
    str
        File path to the corpus file ``demo_corpus.jsonl``
    
    Notes
    -----
    Demo data `download link <https://raw.githubusercontent.com/liao961120/concordancer/main/test-data/demo_corpus.jsonl.zip>`_
    """
    fp = DEMO_DATA.split('/')[-1]
    tgt_dir = pathlib.Path(to).expanduser()

    # Download data
    urllib.request.urlretrieve(DEMO_DATA, fp)
    
    # Extract zip file
    with zipfile.ZipFile(fp, 'r') as zip_ref:
        zip_ref.extractall(tgt_dir)
    os.remove(fp)
    
    out_fp = (tgt_dir / fp.strip('.zip')).absolute()
    print(f"Corpus downloaded to {out_fp}")

    return str(out_fp)