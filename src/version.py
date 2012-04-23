import config
def check_version():
    import gnutr_consts
    if gnutr_consts.DISABLED or not config.get_value('check_version'):
        return
    import time
    interval = config.get_value('check_interval')
    last_check = config.get_value('last_check')
    time_now = time.time()
    if (time_now - last_check > interval):
        import install
        this_ver = install.VERSION
        curr_ver = get_latest_version(gnutr_consts.LATEST_VERSION) 
        update = False
        if this_ver == curr_ver:
            pass  # Nothing to do
        else:
            update = cmp_version_strings(this_ver,curr_ver)
        if update:
            update_version()
    last_check = config.set_key_value('last_check',time_now)

def get_latest_version(url):
    """This needs to be written: fetch posted version at url."""
    import urllib
    import json
    try:
        obj = urllib.urlopen(url)
    except IOError, e:
        print e
        return "0.0" # Force update bypass
    data = obj.read()
     
def cmp_ver_strings(this_ver,curr_ver):
    return False

def update_version():
    pass  # This needs to be written; update to latest version??

if __name__ == '__main__':
    import gnutr_consts
    url = gnutr_consts.LATEST_VERSION
    ver = get_latest_version(url)
