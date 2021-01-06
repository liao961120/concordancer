import os
import json
import cqls
import falcon
import pathlib
import webbrowser
from falcon_cors import CORS
from wsgiref import simple_server
from .concordancer import Concordancer


def run(Concordancer, port=1420, url=None):
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
    webbrowser.open(url)
    httpd.serve_forever()


class ConcordancerBackend(object):
    def __init__(self, Concordancer):
        # Initialize corpus
        self.CONCORDANCE_CACHE = []
        self.C = Concordancer

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
        print("Recieved request!!!")
        ############ _DEBUGGING ##############

        # Test CQL syntax
        cql = params['query']
        try:
            cqls.parse(cql)
        except:
            resp.status = falcon.HTTP_400
            resp.body = 'CQL Syntax error'

        # Query Database
        concord_list = self.C.cql_search(
            cql, left=params['left'], right=params['right']
        )

        # Response to frontend
        ############ DEBUGGING ##############
        print("Sending response...")
        ############ _DEBUGGING ##############
        resp.status = falcon.HTTP_200  # This is the default status
        self.CONCORDANCE_CACHE = concord_list
        resp.body = json.dumps(concord_list, ensure_ascii=False)
        ############ DEBUGGING ##############
        print("Response sent !!!")
        ############ _DEBUGGING ##############

    def on_get_export(self, req, resp):
        # Process concordance to tsv
        resp.body = json.dumps(self.CONCORDANCE_CACHE, ensure_ascii=False, indent="\t")



########################################
##### Code for front-end interface #####
########################################
def download_query_interface(url, force=False):
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
        print(f"frontend interface already exists in {fp}")
        if not force: return

    import zipfile
    import urllib.request
    import concordancer.server

    tgt_dir = pathlib.Path(concordancer.server.__file__).parents[0]

    # Download data
    urllib.request.urlretrieve(url, tgt_dir / "dist.zip")
    
    # Extract zip file
    with zipfile.ZipFile(tgt_dir / "dist.zip", 'r') as zip_ref:
        zip_ref.extractall(tgt_dir)
    
    return tgt_dir
    

def query_interface_path():
    import concordancer.server
    return str(pathlib.Path(concordancer.server.__file__).parents[0] / "dist/index.html")
