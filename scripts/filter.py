import os
import os.path
import re

patterns = [
    # Particular files
    r"apache.conf$",
    r"src/my.cnf$",  
    # General rules
    r"src/.+\.py$",
    r"ENV/.+\.py$",
    r"src/jukebox/templates/.+\.xml",
    r"src/jukebox/static/.+\.(js|css|ico|png|jpg|jpeg|gif|xcf)"
]

def include(path):
    for pattern in patterns:
        if re.search(pattern, path):
            return True
    return False

def filter(path):
    """Returns true iff the path should be included in files to be deployed"""
    return os.path.isdir(path) or include(path)

def filter_dir(dir, files):
    "Returns the files to *ignore*"
    result = []
    for file in files:
        path = os.path.join(dir, file)
        if not filter(path):
            result.append(file)
    return result

def cleanup_dir(dir):
    "Recursively removes empty directories"
    for root, dirs, files in os.walk(dir, topdown=True):
        for dirname in dirs:
            path = os.path.join(root, dirname)
            try:
                os.rmdir(path) # Fails if dir is not empty
            except OSError:
                pass
