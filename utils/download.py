import requests
import cbor
import time

from utils.response import Response

# STUDENT MADE # ADDED TIMEOUT
ESTABLISH_CONNECTION_TIMEOUT = 10 # in seconds
DOWNLOAD_TIMEOUT = 20 # in seconds
TIMEOUT = tuple([ESTABLISH_CONNECTION_TIMEOUT, DOWNLOAD_TIMEOUT])

def download(url, config, logger=None):
    host, port = config.cache_server
    resp = Response({"url" : "", "status" : ""})
    try:
        resp = requests.get(
            f"http://{host}:{port}/",
            params=[("q", f"{url}"), ("u", f"{config.user_agent}")], timeout=TIMEOUT) # STUDENT MADE # ADDED TIMEOUT
        if resp and resp.content:
            return Response(cbor.loads(resp.content))
        else:
            return Response({"url" : "", "status" : ""})
    except (EOFError, ValueError, requests.exceptions.RequestException) as e:
        logger.error(f"Spacetime Response error {resp} with url {url}. Exception: {e}")
        return Response({
            "error": f"Spacetime Response error {resp} with url {url}.",
            "status": resp.status,
            "url": url})
