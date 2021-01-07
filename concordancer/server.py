import os
import json
import cqls
import falcon
import pathlib
import logging
import webbrowser
from urllib.parse import unquote
from falcon_cors import CORS
from wsgiref import simple_server
from .concordancer import Concordancer

FRONTEND_ZIP = 'https://github.com/liao961120/concordancer/raw/query-interface/dist.zip'
URL_ESCAPES = [
    ["{", "___LCURLY_BRACKET___"],
    ["}", "___RCURLY_BRACKET___"],
    ["[", "___LSQUARE_BRACKET___"],
    ["]", "___RSQUARE_BRACKET___"],
    [chr(92), "___BACKSLASH___"],
    ["^", "___START_ANCHOR___"],
    [";", "___SEMICOLON___"],
    ["/", "___SLASH___"],
    ["?", "___QUESTION___"],
    [":", "___COLON___"],
    ["@", "___AT___"],
    ["&", "___AMPERSAND___"],
    ["=", "___EQUAL___"],
    ["+", "___PLUS___"],
    ["$", "___END_ANCHOR___"],
    [",", "___COMMA___"],
]


def run(Concordancer, port=1420, url=None, open_browser=True):
    # Allow access from frontend
    cors = CORS(allow_all_origins=True)

    # Falcon server
    app = falcon.API(middleware=[cors.middleware])
    serv = ConcordancerBackend(Concordancer)
    app.add_route('/query', serv)
    app.add_route('/export', serv, suffix='export')

    print(f"Initializing server...")
    httpd = simple_server.make_server('localhost', port, app)
    print(f"Start serving at http://localhost:{port}")
    if url is None:
        url = query_interface_path()
    if open_browser:
        webbrowser.open(url)
    httpd.serve_forever()


class ConcordancerBackend(object):
    def __init__(self, Concordancer):
        # Initialize corpus
        self.C = Concordancer
        self.concord_list = []

    def on_get(self, req, resp):
        params = {
            'query': '',
            'left': '10',
            'right': '10',
        }
        # Parse query string
        for k, v in req.params.items():
            params[k] = v
        params['left'] = int(params['left'])
        params['right'] = int(params['right'])
        ############ DEBUGGING ##############
        print("Searching corpus...")
        ############ _DEBUGGING ##############

        # Test CQL syntax
        cql = params['query']
        for char, escape in URL_ESCAPES:
            cql = cql.replace(escape, char)
        try:
            cqls.parse(cql)
        except:
            resp.status = falcon.HTTP_400
            resp.body = 'CQL Syntax error'

        # Query Database
        self.concord_list = list(
            self.C.cql_search(
                cql,
                left=params['left'],
                right=params['right']
            )
        )

        # Response to frontend
        ############ DEBUGGING ##############
        print(f"Found {len(self.concord_list)} results...\n")
        ############ _DEBUGGING ##############
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = json.dumps(self.concord_list, ensure_ascii=False)

    def on_get_export(self, req, resp):
        # Process concordance to tsv
        resp.body = json.dumps(list(self.concord_list),
                               ensure_ascii=False, indent="\t")


########################################
##### Code for front-end interface #####
########################################
def download_query_interface(url=None, force=True):
    """Download and extract front-end interface for query

    Parameters
    ----------
    url : str
        URL of the ``dist.zip`` file containing the
        front-end interface for querying
    force : bool, optional
        Force download, by default False
    """
    fp = query_interface_path()
    if os.path.exists(fp):
        logging.info(f"frontend interface already exists in {fp}")
        if not force:
            return

    import zipfile
    import urllib.request
    import concordancer.server

    # Download data
    tgt_dir = pathlib.Path(concordancer.server.__file__).parents[0]
    if url is None:
        url = FRONTEND_ZIP
    urllib.request.urlretrieve(url, tgt_dir / "dist.zip")

    # Extract zip file
    with zipfile.ZipFile(tgt_dir / "dist.zip", 'r') as zip_ref:
        zip_ref.extractall(tgt_dir)

    return tgt_dir


def query_interface_path():
    import concordancer.server
    return str(pathlib.Path(concordancer.server.__file__).parents[0] / "dist/index.html")
