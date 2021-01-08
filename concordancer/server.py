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
    """Serve the concordancer object to allow searching with the web browser

    Parameters
    ----------
    Concordancer : Concordancer
        A concordancer object
    port : int, optional
        The port the server listens on, by default 1420
    url : str, optional
        Custom path to the query interface, by default None, 
        which uses the path to local query interface bundled
        with the library
    open_browser : bool, optional
        Automatically visit the url with the browser, by default True
    """
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
    """Falcon API to serve the concordancer object for the query interface

    Notes
    -----
    Two API endpoints, ``/query`` and ``/export``, are exposed. The endpoint 
    ``/export`` accepts a GET request and responds by sending the most recent
    queried results back to the front-end in JSON format. The data sent back 
    are identical to the data returned by 
    :func:`~concordancer.Concordancer.cql_search` (converted to JSON).
    For the endpoint ``/query``, see the doc in 
    :func:`~server.ConcordancerBackend.on_get`
    """
    def __init__(self, Concordancer):
        # Initialize corpus
        self.C = Concordancer
        self.concord_list = []

    def on_get(self, req, resp):
        """Handling GET requests sent to ``/query``

        Parameters
        ----------
        req : falcon.request
            Refer to falcon's documentation
        resp : falcon.response
            Refer to falcon's documentation
        
        Notes
        -----
        Three parameters, ``query``, ``left``, and ``right`` are required
        in the query string of the URL sent to this endpoint. ``query``
        holds the CQL query entered by the user. ``left`` and ``right`` set
        the left and right context sizes of the returned concordance lines.

        Due to the conflicts between CQL metacharacters and URL specification,
        some characters are replaced with safe ones in the front-end and
        converted back to the original ones in the back-end. For the full set
        of characters converted, refer to `URL_ESCAPES`_.

        .. _URL_ESCAPES: https://github.com/liao961120/concordancer/blob/acd64e6c572e229fe4633d3a415ce1ac45a5b5be/kwic/src/components/kwic.vue#L141-L158
        """
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

        # Restore escaped characters in URL back to original forms
        cql = params['query']
        for char, escape in URL_ESCAPES:
            cql = cql.replace(escape, char)
        # Test CQL syntax
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
        resp.body = json.dumps({
            'results': self.concord_list,
            'default_attr': self.C._cql_default_attr
        }, ensure_ascii=False)

    def on_get_export(self, req, resp):
        """Handling GET requests sent to ``/export``

        Parameters
        ----------
        req : falcon.request
            Refer to falcon's documentation
        resp : falcon.response
            Refer to falcon's documentation
        
        Notes
        -----
        Sends the most recent queried results back to the front-end in JSON
        """
        resp.body = json.dumps(self.concord_list, ensure_ascii=False, indent="\t")


########################################
##### Code for front-end interface #####
########################################
def download_query_interface(url=None, force=True):
    """Download and extract query interface from web

    Parameters
    ----------
    url : str, optional
        URL of the ``dist.zip`` file containing the
        query interface. By default None, which uses
        the default URL specified by the library
    force : bool, optional
        Force download, by default True
    """
    fp = query_interface_path()
    if os.path.exists(fp):
        logging.info(f"query interface already exists in {fp}")
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
    """Get the local path to the query interface

    Returns
    -------
    str
        Path to the query interface
    """
    import concordancer.server
    return str(pathlib.Path(concordancer.server.__file__).parents[0] / "dist/index.html")
