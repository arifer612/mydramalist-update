def save_log(log,title):
    logstr = [str(ep_num)+'\n' for ep_num in log]
    with open('{}_logs.txt'.format(title.replace(' ','_')),'w') as logfile:
        logfile.writelines(logstr)


def open_log(title):
    try:
        with open('{}_logs.txt'.format(title.replace(' ','_')),'r') as logfile:
            updated = [ep.replace('\n', '') for ep in logfile.readlines()]
    except Exception:
        updated = []
    return updated