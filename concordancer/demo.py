import os
import pathlib
import zipfile
import urllib.request

DEMO_DATA = 'https://raw.githubusercontent.com/liao961120/concordancer/main/test-data/demo_corpus.jsonl.zip'


def download_demo_corpus(tgt_dir='.'):
    fp = DEMO_DATA.split('/')[-1]
    tgt_dir = pathlib.Path(tgt_dir).expanduser()

    # Download data
    urllib.request.urlretrieve(DEMO_DATA, fp)
    
    # Extract zip file
    with zipfile.ZipFile(fp, 'r') as zip_ref:
        zip_ref.extractall(tgt_dir)
    os.remove(fp)
    
    print(f"Demo corpus downloaded to {(tgt_dir / fp.strip('.zip')).absolute()}")