from sywek import Create_app
#from sqlalchemy.engine.url import URL,make_url
import os
from pathlib import Path
#import ptvsd
import sys


def load_env_var(mode):
    filename = ''
    if mode == 'dev' or mode == 'development':
        filename = 'env_debug.env'
    else:
        filename = 'env.env'
    filepath = os.path.dirname(os.path.abspath(__file__))+"\\env\\"+filename
    if os.path.isfile(filepath):

        with open(filepath) as evnFile:

            envDir = {key.strip(): val.strip() for key, val in map(
                lambda v: v.split('='), evnFile.read().splitlines())}
            for k, v in envDir.items():
                os.environ[k] = v
    else:

        pass
        # print('Env file not exist : ', filename)

        # if len(sys.argv) >= 1:
        #   load_env_var(mode = sys.argv[1])
        # else:
        #   load_env_var(mode = 'prod')
        # ptvsd.enable_attach()
        #load_env_var(mode = 'dev')
app = Create_app()


if __name__ == '__main__':
    if app.env == 'development':
        app.run(debug=True)
    else:
        pass
        # app.run(host='0.0.0.0', port=80)
