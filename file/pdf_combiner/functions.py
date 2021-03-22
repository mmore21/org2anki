import os.path

def validPDF(file):
    return True if (os.path.exists(file)) else False
