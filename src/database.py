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
import sqlite3 as dbms
import datetime, time
import re

def ticks():
    return time.time()

def curtime():
    """Return current local time as hh:mm"""
    return str(dbms.TimeFromTicks(ticks()))[:5]

def curdate():
    """Return todays date as yyyy-mm-dd"""
    return str(dbms.DateFromTicks(ticks()))

def leap_year(year):
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    if year % 4 == 0:
        return True
    return False

def to_days(datestr):
    #          J  F  M  A  M  J  J  A  S  O  N  D
    months =  [31,28,31,20,31,30,31,31,30,31,30,31]
    ymd = datestr.split('-')
    year = int(ymd[0])
    # We only need to know if we are spanning Feb 29
    # BTW: the next year is 2016
    if leap_year(year):
        months[1] = 29
    days = (year - 1900) * 365; 
    days = days + months[int(ymd[1])] + int(ymd[2])
    return days

dbms.register_adapter(datetime.datetime, curtime)
dbms.register_adapter(datetime.datetime, curdate)

def regexp(exp, text):
    """Define a function to be called when sqlite3 module sees 'REGEXP'"""
    return re.search(exp, text) is not None

class Database:
    _shared_state = {}
    def __init__(self):
        self.__dict__ = self._shared_state
        if self._shared_state:
            return
        self.Error = dbms.Error
        from os import path
        import config
        self.user = config.user
        dbfile =  path.join(config.udir, 'gnutr_db.lt3')
        try:
            con = dbms.connect(dbfile)
            # text_factory must be set to 'str' due to current limitations
            # in csv.reader()
            con.text_factory = str
            con.create_function('REGEXP', 2, regexp)
            con.create_function('TO_DAYS', 1, to_days)
            cur = con.cursor()
        except self.Error, e:
            "Error {0:s}:".format(e.args[0])
            raise self.Error
        self.con = con
        self.cur = cur

    def close(self): 
        if self.con:
            self.con.close()

    def initialize(self):
        # Create Food Description (food_des) table.
        # Data file FOOD_DES.
        self.query("DROP TABLE IF EXISTS food_des")
        self.create_load_table("CREATE TABLE food_des" +
            "(NDB_No INTEGER NOT NULL, " + 
            "FdGrp_Cd INTEGER NOT NULL, " + 
            "Long_Desc TEXT NOT NULL, " + 
            "Shrt_Desc TEXT NOT NULL, " + 
            # Three new fields for sr24
            "ComName TEXT, " + 
            "ManufacName TEXT, " +
            "Survey TEXT, " +
            # end new
            "Ref_desc TEXT, " + 
            "Refuse INTEGER, " + 
            "SciName TEXT, " + 
            "N_Factor REAL, " +
            "Pro_Factor REAL, " + 
            "Fat_Factor REAL, " + 
            "CHO_Factor REAL, " +
            "PRIMARY KEY(NDB_No, FdGrp_Cd))",
            ### Insert statement
            "INSERT INTO 'food_des' VALUES " +
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            'food_des')

        # Create Food Group Description (fd_group) table.
        # Data file FD_GROUP.
        self.query("DROP TABLE IF EXISTS fd_group")
        self.create_load_table("CREATE TABLE fd_group " + 
            "(FdGrp_Cd INTEGER PRIMARY KEY NOT NULL, " + 
            "FdGrp_Desc TEXT NOT NULL)",
            ### Insert statement for one row
            "INSERT INTO 'fd_group' VALUES (?, ?)",
            'fd_group')

        # Create Nutrient Data (nut_data) table.
        # Data file NUT_DATA
        self.query("DROP TABLE IF EXISTS nut_data")
        self.create_load_table("CREATE TABLE nut_data " + 
            "(NDB_No INTEGER NOT NULL, " + 
            "Nutr_No INTEGER NOT NULL, " + 
            "Nutr_Val REAL NOT NULL, " + 
            "Num_Data_Pts REAL NOT NULL, " + 
            "Std_Error REAL, " + 
            "Src_Cd TEXT NOT NULL, " +
            "Deriv_Cd TEXT, " +
            "Ref_NDB_No TEXT, " +
            "Add_Nutr_Mark TEXT, " +
            "Num_Studies INTEGER, " +
            "Min REAL, " +
            "Max REAL, " +
            "DF INTEGER, " +
            "Low_EB REAL, " +
            "Up_EB REAL, " +
            "Stat_cmt TEXT, " +
            "AddMod_Date TEXT, " +
            "CC TEXT, " +
            "PRIMARY KEY(NDB_No, Nutr_No))",
            ### Insert statement for one row
            "INSERT INTO 'nut_data' VALUES " +
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            'nut_data') 

        # Create Nutrient Definition (nutr_def table.
        # Data file NUTR_DEF
        self.query("DROP TABLE IF EXISTS nutr_def")
        self.create_load_table("CREATE TABLE nutr_def " + 
            "(Nutr_No INTEGER PRIMARY KEY NOT NULL, " + 
            "Units TEXT NOT NULL, " +
            "Tagname TEXT, " +
            "NutrDesc TEXT NOT NULL, " +
            # Two new in sr24
            "Num_Dec INTEGER NOT NULL, " +
            "SR_Order INTEGER NOT NULL)",
            ### Insert statement for one row
            "INSERT INTO 'nutr_def' VALUES " +
            "(?, ?, ?, ?, ?, ?)",
            'nutr_def')

        # Create temporary weight table.
        # Data file WEIGHT.
        self.query("DROP TABLE IF EXISTS weight")
        self.create_load_table("CREATE TABLE weight" +
            "(NDB_No INTEGER NOT NULL, " +
            # Seq == Sequence number for measure description (Msre_Desc)
            # The NDB_No for a food item will appear once for each measure
            # description. Measure descriptions are sequenced. For example:
            # NDB_No Seq Amount Msre_Desc                Gm_wgt
            # 01001   1    1     cup                       227
            # 01001   2    1     tbsp                       14.2
            # 01001   3    1     pat (1" sq, 1/3" high)      5.0
            # 01001   4    1     stick                     113
            "Seq INTEGER NOT NULL, " +
            # Amount == Unit modifier (for example, 1 in "1 cup").
            "Amount REAL NOT NULL, " +
            "Msre_Desc TEXT NOT NULL, " +
            "Gm_wgt REAL NOT NULL, " +
            "Num_Data_Pts INTEGER, " +
            "Std_Dev REAL, " +
            "PRIMARY KEY(NDB_No, Seq))",
            ### Insert statement for one row
            "INSERT INTO 'weight' VALUES " +
            "(?, ?, ?, ?, ?, ?, ?)",
            'weight')

        # May have user data from previous install that we don't want to lose
        # so IF NOT EXISTS is used

        # create recipe table
        # Note: Want index on recipe_name, category_no?
        self.create_table("CREATE TABLE IF NOT EXISTS recipe" +
            "(recipe_no INTEGER PRIMARY KEY AUTOINCREMENT, " +
            "recipe_name TEXT NOT NULL, " +
            "no_serv INTEGER NOT NULL, " +
            "no_ingr INTEGER NOT NULL, " +
            "category_no INTEGER NOT NULL)", 'recipe') 

        # create ingredient table
        self.create_table("CREATE TABLE IF NOT EXISTS ingredient" + 
            "(recipe_no INTEGER NOT NULL, " + 
            "amount REAL NOT NULL, " +
            "Msre_Desc TEXT NOT NULL, " +
            "NDB_No INTEGER NOT NULL)", 'ingredient')

        # create recipe category table
        self.create_load_table("CREATE TABLE IF NOT EXISTS category" +
            "(category_no INTEGER PRIMARY KEY NOT NULL, " +
            "category_desc TEXT NOT NULL)",
            ### Insert statement
            "INSERT INTO 'category' VALUES (?, ?)",
            'category')

        # create recipe preparation table
        self.create_table("CREATE TABLE IF NOT EXISTS preparation" +
            "(recipe_no INTEGER PRIMARY KEY NOT NULL, " +
            "prep_time TEXT, " +
            "prep_desc TEXT)", 'preparation')

        # create person table
        self.create_table("CREATE TABLE IF NOT EXISTS person" +
            "(person_no INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL," +
            "person_name TEXT, " +
            "user_name TEXT)", 'person')

        # create food_plan table
        self.create_table("CREATE TABLE IF NOT EXISTS food_plan" +
            "(person_no INTEGER NOT NULL, " +
            "date TEXT NOT NULL, " +
            "time TEXT NOT NULL, " +
            "amount REAL NOT NULL, " +
            "Msre_Desc TEXT NOT NULL, " +
            "NDB_No INTEGER NOT NULL)", 'food_plan')

        # create recipe_plan table
        self.create_table("CREATE TABLE IF NOT EXISTS recipe_plan" +
            "(person_no INTEGER NOT NULL, " +
            "date TEXT NOT NULL, " +
            "time TEXT NOT NULL, " +
            "no_portions REAL NOT NULL, " +
            "recipe_no INTEGER NOT NULL)", 'recipe_plan')

        # create nutr_goal table
        self.create_table("CREATE TABLE IF NOT EXISTS nutr_goal" +
            "(person_no INTEGER NOT NULL, " +
            "Nutr_No INTEGER NOT NULL, " +
            "goal_val REAL NOT NULL)", 'nutr_goal')

        return 1

    def curtime(self):
        return curtime()

    def curdate(self):
        return curdate()

    def show_query(self, sql, sql_params, caller=None):
        if not caller: return
        s = ''
        if caller: s = '{0:s}(): '.format(caller)
        s = s + '{0:s}'.format(sql)
        if sql_params:
            s = s + '\n\tparams:'
            print s, sql_params
        else:
            print s

    def query(self, sql, many=False, sql_params=None, caller=None):
        """Execute the SQL statement with given SQL parameters."""
        try:
            if sql_params:
                if many:
                    self.cur.executemany(sql, sql_params)
                else:
                    self.cur.execute(sql, sql_params)
            elif many:
                self.cur.executemany(sql)
            else:
                self.cur.execute(sql)
            self.con.commit()
            result = self.cur.fetchall()
        except self.Error, sqlerr:
            self.con.rollback()
            import sys
            print 'Error :', sqlerr, '\nquery:', sql
            if caller: print 'Caller ', caller
            sys.exit()
        # Convert to tuple as GNUtrition code expects MySQLdb tuple return
        self.result = tuple(result)
        self.last_query = sql
        self.last_query_params = sql_params
        # Added for debugging
        self.show_query(sql, sql_params, caller)

    def get_result(self):
        result = self.result
        self.result = None
        if not result:
            print 'No result from:'
            print 'sql:', self.last_query
            if self.last_query_params:
                print 'sql params:', self.last_query_params
        return result

    def get_row_result(self):
        result = self.result
        self.result = None
        if not result:
            print 'No result from:'
            print 'sql:', self.last_query
            if self.last_query_params:
                print 'sql params:', self.last_query_params
            return None
        if len(result) == 1:
            return result[0]
        print 'Error: not a single row'
        return None

    def get_single_result(self):
        result = self.result
        self.result = None
        if not result:
            print 'No result from:'
            print 'sql:', self.last_query
            if self.last_query_params:
                print 'sql params:', self.last_query_params
            return None
        if len(result) == 1:
            if len(result[0] ) == 1:
                return result[0][0]
        print 'Error: not a single value'
        return None

    def create_table(self, sql, tablename):
        self.query(sql)
        print "created table '{0:s}'".format(tablename)

    def load_table(self, sql, data_fn):
        #self.query("LOAD DATA LOCAL INFILE '"+ fn + "' " +
        #    "INTO TABLE " + table + " FIELDS TERMINATED BY '^'")
        import csv
        try:
            data = csv.reader(open(data_fn,'r'), delimiter='^', quotechar="'")
        except Exception, e:
            print "Failed to read data file '{0:s}'".format(data_fn)
            return False
        self.query(sql, many=True, sql_params=data)
        return True

    def create_load_table(self, create_sql, insert_sql, table_name):
        """Create and load table from file.
        'create_sql' is the SQL statement for table creation.
        'insert_sql' is the SQL statement given to executemany.
        'table_name' serves as both the database table name and the data file name.
        """
        import install
        from os import path
        self.create_table(create_sql, table_name)
        data_file = path.join(install.idir, 'data', table_name.upper() + '.txt')
        if self.load_table(insert_sql, data_file):
            print "loaded table '{0:s}'".format(table_name)
        else:
            print "failed to load table '{0:s}'".format(table_name)

    def add_user(self, user, password):
        self.query("GRANT USAGE ON *.* TO " + user +
            "@localhost IDENTIFIED BY '" + password + "'")
        self.query("GRANT ALL ON gnutr_db.* TO " + user + 
            "@localhost IDENTIFIED BY '" + password + "'")
        self.query("FLUSH PRIVILEGES")

    def delete_db(self):
        self.query("DROP DATABASE gnutr_db")

    def next_row(self, col, table):
        self.query("SELECT MAX({0:s}) from {1:s}".format(col, table))
        m = self.get_single_result()
        if not m:
            m = 1
        else:
            m += 1
        return m

def migrate(mysql):
    """Retrieve gnutrition table data from MySQL database.
    Parameters uname and pword are the MySQL username and password used with
    the older version of GNUtritin."""
    from gnutr import Dialog
    lite = Database()

    # Need to check for tables: recipe, ingredient, preparation
    # person, food_plan, recipe_plan, nutr_goal 
    tables = ['recipe', 'ingredient', 'preparation','person',
              'food_plan', 'recipe_plan']
    mysql.query('SHOW TABLES')
    old_tables = mysql.get_result()
    # At some point use of a 'measure' table was discontinued
    use_msre_no = False
    found = []
    for t in old_tables:
        if t[0] in tables:
            found.append(t[0])
        if t[0] == 'measure':
            use_msre_no = True

    # Quirks:
    # 0.31 does not save recipe or food_plan (nothing to migrate except 
    #      person data.
    # 0.31.1 uses fd_no (for NDB_No) and msre_no to index measure table
    # 0.32 onward uses NDB_No and Msre_Desc (no measure table)

    # For gnutrition version < 0.32
    def msre_desc_from_msre_no(msre_no):
        sql = "SELECT msre_desc FROM measure WHERE msre_no = {0:d}"
        mysql.query(sql.format(msre_no))
        return mysql.get_single_result()

    # recipie table
    if 'recipe' in found:
        mysql.query("SELECT recipe_no, recipe_name, no_serv, no_ingr, " +
                    "category_no FROM recipe")
        result = mysql.get_result()
        if result and len(result) > 0:
            print 'found', len(result), 'recipies'
            print result
            lite.query("INSERT INTO 'recipe' VALUES (?,?,?,?,?)",
                           many=True, sql_params=result, caller='migrate')
    # ingredient table
    if 'ingredient' in found:
        sql1 = "SELECT recipe_no, amount, msre_no, fd_no FROM ingredient"
        sql2 = "SELECT recipe_no, amount, Msre_Desc, NDB_No FROM ingredient"
        if use_msre_no:
            mysql.query(sql1)
        else:
            mysql.query(sql2)
        result = mysql.get_result()
        if result:
            print 'found', len(result), 'ingredients'
            print result
            for i in range(len(result)):
                recipe_no = result[i][0]
                amount = result[i][1]
                if use_msre_no:
                    Msre_Desc = msre_desc_from_msre_no(result[i][2])
                else:
                    Msre_Desc = result[i][2]
                NDB_No = result[i][3]
                params = (recipe_no, amount, Msre_Desc, NDB_No)
                lite.query("INSERT INTO 'ingredient' VALUES (?,?,?,?)",
                           many=False, sql_params=params, caller='migrate')

    # preparation table
    if 'preparation' in found:
        mysql.query("SELECT recipe_no, prep_time, prep_desc FROM preparation")
        result = mysql.get_result()
        if result and len(result) > 0:
            print 'found', len(result), 'entries in preparation table'
            print result
            lite.query("INSERT INTO 'preparation' VALUES (?,?,?)",
                           many=True, sql_params=result, caller='migrate')

    # person table
    if 'person' in found:
        mysql.query("SELECT person_no, person_name, user_name FROM person")
        result = mysql.get_result()
        if result and len(result) > 0:
            print 'found', len(result), 'entries in person table'
            print result
            lite.query("INSERT INTO 'person' VALUES (?,?,?)",
                           many=True, sql_params=result, caller='migrate')

    # food_plan table
    if 'food_plan' in found:
        sql1 = "SELECT person_no, date, time, amount, msre_no, fd_no FROM food_plan"
        sql2 = "SELECT person_no, date, time, amount, Msre_Desc, NDB_No FROM food_plan"
        if use_msre_no:
            mysql.query(sql1)
        else:
            mysql.query(sql2)
        result = mysql.get_result()
        if result and len(result) > 0:
            print 'found', len(result), 'entries in food_plan table'
            for i in range(len(result)):
                person_no = result[i][0]
                date = str(result[i][1])
                time = str(result[i][2])
                amount = result[i][3]
                if use_msre_no:
                    Msre_Desc = msre_desc_from_msre_no(result[i][4])
                else:
                    Msre_Desc = result[i][4]
                NDB_No = result[i][5]
                params = (person_no, date, time[:-3], amount, Msre_Desc, NDB_No)
                lite.query("INSERT INTO 'food_plan' VALUES (?,?,?,?,?,?)",
                           many=False, sql_params=params, caller='migrate')
    # recipe_plan table
    if 'recipe_plan' in found:
        # Need to convert datetime.date and datetime.timedelta MySQL types to
        # strings before inserting into SQLite table.
        mysql.query("SELECT person_no, date, time, no_portions, " +
                    "recipe_no FROM recipe_plan")
        result = mysql.get_result()
        print 'found', len(result), 'entries in recipe_plan table'
        if result and len(result) > 0:
            for r in range(len(result)):
                person_no = result[r][0]
                date = str(result[r][1])
                time = str(result[r][2])
                no_portions = result[r][3]
                recipe_no = result[r][4]
                params = (person_no, date, time[:-3], no_portions, recipe_no)
                print params
                lite.query("INSERT INTO 'recipe_plan' VALUES (?,?,?,?,?)",
                           many=False, sql_params=params, caller='migrate')
    # nutr_goal table needs to be recalculated
    return True
#---------------------------------------------------------------------------
if __name__ == '__main__':
    print 'curdate:', curdate()
    print 'curtime:', curtime()
