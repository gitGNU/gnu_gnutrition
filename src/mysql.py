# GNUtrition - a nutrition and diet analysis program.
# Copyright (C) 2000-2002 Edgar Denny (edenny@skyweb.net)
# Copyright (C) 2010 2012 Free Software Foundation, Inc.
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

import MySQLdb
import warnings

class Database:
    _shared_state = {}
    def __init__(self, uname=None, pword=None):
        self.__dict__ = self._shared_state
        if self._shared_state:
            return
    # supress warning on "DROP TABLE IF EXISTS" for temp tables
        warnings.filterwarnings("ignore", "Unknown table.*_temp")
    # supress 'Data truncated ...' 
        warnings.filterwarnings("ignore", "Data truncated*")

        self.db = MySQLdb.Connect(user=uname, passwd=pword)
        self.cursor = self.db.cursor()
        self.user = uname
        self.rows = 0
        self.result = None
 
    def change_user(self, uname, pword, dbase): 
        try:
            self.db = MySQLdb.Connect(user=uname, passwd=pword, db=dbase)
            self.cursor = self.db.cursor()
            self.user = uname
        except:
            return 0
        return 1

    def initialize(self):
        self.query('SHOW DATABASES')
        db_list = self.get_result()
        for b in db_list:
            if b[0] == 'gnutr_db':
                self.query('USE gnutr_db')
                return True
        return False

    def query(self, query, caller=None):
        try:
            self.cursor.execute(query)
        except MySQLdb.Error, sqlerr:
            print 'Error :', sqlerr, '\nquery:', query
            self.cursor.execute('SHOW ERRORS');
            import traceback
            import sys
            traceback.print_exc()
            if caller: print 'Caller ', caller
            sys.exit()
        self.result = self.cursor.fetchall()
        self.rows = self.db.affected_rows()
        self.db.commit()
#        return self.get_result()

    def get_result(self):
        result = self.result
        self.result = None
        if not result:
            print 'No result'
        return result

    def get_row_result(self):
        result = self.result
        self.result = None
        if not result:
            print 'No result'
            return None
        if len(result) == 1:
            return result[0]
        print 'Error: not a single row'
        return None

    def get_single_result(self):
        result = self.result
        self.result = None
        if not result:
            print 'No result'
            return None
        if len(result) == 1:
            if len(result[0] ) == 1:
                return result[0][0]
        print 'Error: not a single value'
        return None

    def create_table(self, query, tablename):
        self.query(query)
        print "table created: ", tablename

    def load_table(self, fn, table):
        self.query("LOAD DATA LOCAL INFILE '"+ fn + "' " +
            "INTO TABLE " + table + " FIELDS TERMINATED BY '^'")

    def create_load_table(self, query, filename):
        import install
        from os import path
        self.create_table(query, filename)
        fn = path.join(install.idir,'data',filename.upper() + '.txt')
        self.load_table(fn, filename)
        print "table loaded: ", filename

    def add_user(self, user, password):
        self.query("GRANT USAGE ON *.* TO " + user +
            "@localhost IDENTIFIED BY '" + password + "'")
        self.query("GRANT ALL ON gnutr_db.* TO " + user + 
            "@localhost IDENTIFIED BY '" + password + "'")
        self.query("FLUSH PRIVILEGES")

    def delete_db(self):
        self.query("DROP DATABASE gnutr_db")

    def user_setup(self, uname, pword):
        # check to see if user name is already in mysql.user and that the
        # password is correct
        if self.user_name_exists(uname):
            if self.password_match(uname, pword):
                # add the info to the config file.
                #config.set_key_value('Username', uname)
                #config.set_key_value('Password', pword)
                # check to see if user can access 'gnutr_db'
                if not self.user_db_access(uname):
                    # grant privileges to user
                    self.mysql.add_user(uname, pword)
            else:
                # HERE: add dialog notifying that ...
                return 0
        else:
            # HERE: add dialog notifying that ...
            return 0
        return 1

    def user_name_exists(self, uname):
        self.mysql.query("USE mysql")
        self.mysql.query("SELECT User FROM user WHERE " +
            "User = '" + uname + "'")
        name = self.mysql.get_single_result()
        if not name:
            return 0
        return 1

    def password_match(self, uname, pword):
        # check to see if the password is correct
        self.mysql.query("SELECT Password FROM user WHERE " +
            "User = '" + str(uname) + "'")
        result1 = self.mysql.get_single_result()
        self.db.query("SELECT PASSWORD('" + str(pword) + "')")
        result2 = self.mysql.get_single_result()
        if result1 == result2:
            return 1;
        return 0

    def user_db_access(self, uname):
        # does the user have access to the gnutr_db?
        self.mysql.query("SELECT Db FROM db WHERE " +
            "User = '" + str(uname) + "'")
        result = self.mysql.get_result()
        for db_name in result:
            if db_name[0] == 'gnutr_db':
                return 1
        return 0
