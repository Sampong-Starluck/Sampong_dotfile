from urllib import request

def internet_on(url: str):
    print(f"[INFO] Checking internet on {url}")
    try:
        request.urlopen(url, timeout=1)
        return True
    except request.URLError as err:
        print(err)
        return False
