'''
This script can be used to manually load beatmaps into the game
It should not be needed.
'''

import sys
from zipfile import ZipFile

def main():
    argv = sys.argv

    for arg in argv:
        try:
            with ZipFile(arg) as file:
                name = file.filename
                name = name[0:-4]
                file.extractall(f"beatmaps/{name}")
        except:
            continue
if __name__ == "__main__":
    main()