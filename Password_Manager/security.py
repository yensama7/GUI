import hashlib

def hash_maker(webby):
    h = hashlib.sha256()
    h.update(webby.encode('utf-8'))
    hashed = h.hexdigest()
    return hashed

