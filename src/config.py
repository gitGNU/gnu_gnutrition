#  GNUtrition - a nutrition and diet analysis program.
#  Copyright(C) 2000 - 2002 Edgar Denny (edenny@skyweb.net)
#  Copyright (C) 2012 Free Software Foundation, Inc.
#  Copyright (C) 2013 Adam 'foo-script' Rakowski (fooscript att o2 dott pl)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import shelve, install
from os import environ, path, access, F_OK, mkdir, name

if name == 'nt':
	home = environ['USERPROFILE']
else: 
	home = environ['HOME']

user = path.basename(home)
udir = path.join(home, '.gnutrition', install.gnutr_version())
fn = path.join(udir, 'config')
if not access(udir, F_OK):
    mkdir(udir)

def get_value(key):
    db = shelve.open(fn, 'c')
    try:
        value = db[key]
    except KeyError:
        value = None
    db.close()
    return value

def set_key_value(key, value):
    db = shelve.open(fn)
    db[key] = value
    db.close()

def delete_entry(key):
    db = shelve.open(fn)
    if db.has_key[key]:
        del db[key]
    db.close()

def keys():
    from util.utility import stdout
    db = shelve.open(fn)
    for key in db.keys():
        stdout("{0:s}: {1!r}\n".format(key, db[key]))
    db.close()

if __name__ == '__main__':
    print 'Current keys in', fn
    keys()
    print
