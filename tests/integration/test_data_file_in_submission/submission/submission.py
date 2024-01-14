def readFile(path) -> str:
    with open(path, "r") as r:
        return r.read().strip()
