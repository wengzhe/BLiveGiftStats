import os
import sys
sys.path.insert(0, os.path.split(os.path.realpath(__file__))[0])

from web_app import app as application

if __name__ == '__main__':
    application.run(host='::', debug=True)
