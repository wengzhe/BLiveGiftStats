import os
import sys
os.chdir(os.path.dirname(os.path.realpath(__file__)))

from web_app import app as application

if __name__ == '__main__':
    application.run(host='::', debug=True)
