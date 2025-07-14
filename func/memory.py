data = {}

def put(key: str, value):
    global data
    data[key] = value

def get(key: str, default=None):
    global data
    return data.get(key, default)