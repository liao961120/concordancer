import logging
from concordancer.server import download_query_interface

try:
    download_query_interface(force=True)
except:
    logging.warning("Skip download query interface")