import configparser
import logging
import os
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run(['python3',
                    f'{os.getcwd()}/app.py',
                    sys.argv[1]],
                   capture_output=False)
