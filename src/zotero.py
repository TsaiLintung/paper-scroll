import os, time, uuid, json, requests, pathlib

Z_HOST  = "http://127.0.0.1:23119"      # Zotero desktop
T_HOST  = "http://127.0.0.1:1969"       # translation-server
HEADERS = {"X-Zotero-Connector-API-Version": "3"}   # required on every /connector call

def _doi_to_item(doi:str)->dict:
    r = requests.post(f"{T_HOST}/search", data=doi, headers={"Content-Type":"text/plain"}, timeout=60)
    r.raise_for_status()
    return r.json()[0]                  # translation-server returns an array

def _save_in_zotero(item:dict)->str:
    payload = {
        "sessionID": str(uuid.uuid4()),
        "items":     [item]             # /connector/saveItems expects an array
    }
    r = requests.post(f"{Z_HOST}/connector/saveItems",
                      json=payload, headers=HEADERS, timeout=60)
    r.raise_for_status()
    # On success Zotero returns 201 and the parent key in Location, but easiest is:
    print(f"Zotero item saved: {item['key']}")
    return item["key"]                  # the key the translator already gave us

def _wait_for_pdf(parent_key:str, timeout=90)->str:
    t0=time.time()
    while time.time()-t0 < timeout:
        kids = requests.get(f"{Z_HOST}/api/users/0/items/{parent_key}/children",
                            params={"format":"json"}, timeout=10).json()
        for k in kids:
            if k["data"].get("contentType") == "application/pdf":
                return k["key"]
        time.sleep(1)
    raise TimeoutError("No PDF attached within the time-out window")

def _get_local_file(item_key:str)->str:
    r = requests.get(f"{Z_HOST}/api/users/0/items/{item_key}/file",
                     allow_redirects=False, timeout=10)
    if r.status_code!=302:
        raise RuntimeError("Expected 302 redirect from /file")
    return pathlib.Path(r.headers["Location"].replace("file://","")).as_posix()

def getPDF(doi:str, wait:int=90)->str:
    """
    Add DOI to Zotero (using Zotero’s own translators) and
    return the absolute path of the PDF once Zotero has grabbed it.
    """
    item   = _doi_to_item(doi)
    parent = _save_in_zotero(item)
    attach = _wait_for_pdf(parent, timeout=wait)
    return _get_local_file(attach)

# --- quick test ---
if __name__ == "__main__":
    print(getPDF("10.1038/s41586-020-2649-2"))
