# log.py retrieves and saves the log file. The default directory to create/save the log file would be in the
from .Lib import library


def retrieve(title,dir=''):
    library.directory()
    try:
        with open('{}\\logs\\{}_MDL.txt'.format(dir,title.replace(' ','_')),'r') as logfile:
            updated = [ep.replace('\n', '') for ep in logfile.readlines()]
    except Exception:
        updated = []
    return updated


def save(log,title,dir=''):
    library.directory()
    logstr = [str(ep_num)+'\n' for ep_num in log]
    with open('{}\\logs\\{}_MDL.txt'.format(dir,title.replace(' ','_')),'w') as logfile:
        logfile.writelines(logstr)