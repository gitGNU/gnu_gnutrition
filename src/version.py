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
    import re
    try:
        obj = urllib.urlopen(url)
    except IOError, e:
        print e
        return "0.0" # Force update bypass
    reexp = r"""["]version":\s*["](?P<version>([0-9]+[.]?)+)["]"""
    data = obj.read()
    m = re.search(reexp, data)
    if m:
        return m.group('version')
    return '0.0'

def cmp_ver_strings(this_ver,curr_ver):
    s1 = this_ver.split('.')
    len_s1 = len(s1)
    s2 = curr_ver.split('.')
    len_s2 = len(s2)
    loop = 0
    while loop < len_s1 and loop < len_s2:
        s1_n, s2_n  = int(s1[loop]), int(s2[loop])
        if s1_n < s2_n:
            return True 
        elif s1_n > s2_n:
            return False  # Web version file needs updating
        loop += 1
    # Matched up to this point. Now need to check the case where one version
    # string is longer than the other
    if len_s2 > len_s1:
        return True
    return False

def update_version():
    pass  # This needs to be written; update to latest version??

if __name__ == '__main__':
    import gnutr_consts
    url = gnutr_consts.LATEST_VERSION
    ver = get_latest_version(url)
    print 'latest version available:', ver
    print 'True ==', cmp_ver_strings("0.1", "0.2")
    print 'True ==', cmp_ver_strings("0.1.1", "0.2")
    print 'False ==', cmp_ver_strings("0.2.1", "0.2")
    print 'False ==', cmp_ver_strings("0.2", "0.1")
    print 'True ==', cmp_ver_strings("0.1", "0.2.1")
    print 'True ==', cmp_ver_strings("0.1.1", "0.1.2")
    print 'False ==', cmp_ver_strings("0.2.1", "0.2")
