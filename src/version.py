# Copyright (C) 2012 Free Software Foundation, Inc.
#
# This file is part of GNUtrition.
# 
# GNUtrition is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GNUtrition is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNUtrition.  If not, see <http://www.gnu.org/licenses/>.

import config
def get_latest_version(url):
    """Fetch latest version information posted at URL provided."""
    import urllib
    import re
    try:
        obj = urllib.urlopen(url)
    except IOError, e:
        print e
        return "0.0" # Force update bypass
    reex = r"""
            version"[\s+]?:    #   version":
            [\s+]?"            #  leading junk
            (?P<version>([0-9]+[.]?)+)  # target match
            ["][\s+]?,(.+)?$   #  trailing junk until end of line
            .*"                #  leading junk
            message"[\s+]?:    #  message":
            [\s+]?"            #  eat white space
            (?P<message>.*\.)["]  # target match
            """
    reobj = re.compile(reex, re.X|re.M|re.S)
    m = re.search(reobj, obj.read())
    if m:
        return (m.group('version'), m.group('message'))
    return ('0.0', None)

def cmp_version_strings(this_ver, curr_ver):
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

def update_version(version, message=None):
    """Present user with dialog notification of available newer version."""
    import gnutr
    msg = 'Version {0:s} of gnutrition is available.\n'.format(version)
    msg += 'Please visit http://www.gnu.org/software/gnutrition to download.\n'
    if message:
        msg += '\n{0:s}'.format(message)
    gnutr.Dialog('notify', msg)

def check_version():
    import gnutr_consts
    if config.get_value('check_disabled') or not config.get_value('check_version'):
        return
    import time
    interval = config.get_value('check_interval')
    last_check = config.get_value('last_check')
    time_now = time.time()
    if (time_now - last_check > interval):
        import install
        this_ver = install.VERSION
        (curr_ver, mesg) = get_latest_version(gnutr_consts.LATEST_VERSION) 
        update = False
        if this_ver == curr_ver:
            pass  # Nothing to do
        else:
            update = cmp_version_strings(this_ver,curr_ver)
        if update:
            update_version(curr_ver, mesg)
    last_check = config.set_key_value('last_check',time_now)

if __name__ == '__main__':
    def str_cmp_test():
        print 'True ==', cmp_ver_strings("0.1", "0.2")
        print 'True ==', cmp_ver_strings("0.1.1", "0.2")
        print 'False ==', cmp_ver_strings("0.2.1", "0.2")
        print 'False ==', cmp_ver_strings("0.2", "0.1")
        print 'True ==', cmp_ver_strings("0.1", "0.2.1")
        print 'True ==', cmp_ver_strings("0.1.1", "0.1.2")
        print 'False ==', cmp_ver_strings("0.2.1", "0.2")
    import gnutr_consts
    url = gnutr_consts.LATEST_VERSION
    (ver,msg) = get_latest_version(url)
    print 'latest version available:', ver
    print 'version message:', msg
    #str_cmp_test()
