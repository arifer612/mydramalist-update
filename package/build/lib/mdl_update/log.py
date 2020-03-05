# log.py retrieves and saves the log file. The default directory to create/save the log file would be in the
from . import library
import os


def retrieve(title,dir='.',tail=None,py_dir=os.getcwd()):
    library.directory(py_dir)
    try:
        with open('{}\\logs\\{}{}.txt'.format(dir,title.replace(' ','_'),'_'+tail if tail else ''),'r') as logfile:
            updated = [ep.replace('\n', '') for ep in logfile.readlines()]
    except Exception:
        updated = []
    return updated


def save(log,title,dir='.',tail=None,py_dir=os.getcwd()):
    library.directory(py_dir)
    logstr = [str(ep_num)+'\n' for ep_num in log]
    with open('{}\\logs\\{}{}.txt'.format(dir,title.replace(' ','_'),'_'+tail if tail else ''),'w') as logfile:
        logfile.writelines(logstr)