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

def ticks():
    return time.time()

def curtime():
    """Return current local time as hh:mm"""
    return str(dbms.TimeFromTicks(ticks()))[:5]

def curdate():
    """Return todays date as yyyy-mm-dd"""
    return str(dbms.DateFromTicks(ticks()))

dbms.register_adapter(datetime.datetime, curtime)
dbms.register_adapter(datetime.datetime, curdate)

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
        dbfile =  path.join(config.udir, 'gnutr_db')
        try:
            self.db = dbms.connect(dbfile)
        except self.Error, e:
            "Error {0:s}:".format(e.args[0])
            raise self.Error
        else:
            # text_factory must be set to 'str' due to current limitations
            # in csv.reader()
            self.db.text_factory = str
            self.cursor = self.db.cursor()
            self.rows = 0
            self.result = None

    def initialize(self):
        # Create Food Description (food_des) table.
        # Data file FOOD_DES.
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
        self.create_load_table("CREATE TABLE fd_group " + 
            "(FdGrp_Cd INTEGER PRIMARY KEY NOT NULL, " + 
            "FdGrp_Desc TEXT NOT NULL)",
            ### Insert statement
            "INSERT INTO 'fd_group' VALUES (?, ?)",
            'fd_group')

        # Create Nutrient Data (nut_data) table.
        # Data file NUT_DATA
        self.create_load_table("CREATE TABLE nut_data " + 
            "(NDB_No INTEGER NOT NULL, " + 
            "Nutr_No INTEGER NOT NULL, " + 
            "Nutr_Val REAL NOT NULL, " + 
            "Num_Data_Pts REAL NOT NULL, " + 
            "Std_Error REAL, " + 
            "Src_Cd TEXT NOT NULL, " +
            # New fields in sr24
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
            ### Insert statement
            "INSERT INTO 'nut_data' VALUES " +
            "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            'nut_data') 

        # Create Nutrient Definition (nutr_def table.
        # Data file NUTR_DEF
        self.create_load_table("CREATE TABLE nutr_def " + 
            "(Nutr_No INTEGER PRIMARY KEY NOT NULL, " + 
            "Units TEXT NOT NULL, " +
            "Tagname TEXT, " +
            "NutrDesc TEXT NOT NULL, " +
            # Two new in sr24
            "Num_Dec INTEGER NOT NULL, " +
            "SR_Order INTEGER NOT NULL)",
            ### Insert statement
            "INSERT INTO 'nutr_def' VALUES " +
            "(?, ?, ?, ?, ?, ?)",
            'nutr_def')

        # Create temporary weight table.
        # Data file WEIGHT.
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
            "Msre_No INTEGER NOT NULL, " +
            "Gm_wgt REAL NOT NULL, " +
            "PRIMARY KEY(NDB_No, Seq))",
            ### Insert statement
            "INSERT INTO 'weight' VALUES " +
            "(?, ?, ?, ?, ?)",
            'weight')

        # create measure table
        self.create_load_table("CREATE TABLE measure " +
            "(Msre_No INTEGER PRIMARY KEY NOT NULL, " +
            "Msre_Desc TEXT NOT NULL)",
            "INSERT INTO 'measure' VALUES (?, ?)",
            'measure')

        # create recipe table
        # HERE: recipe_no had AUTOINCREMENT but barfs on the syntax
        self.create_table("CREATE TABLE recipe " +
            "(recipe_no INTEGER NOT NULL, " +
            "recipe_name TEXT NOT NULL, " +
            "no_serv INTEGER NOT NULL, " +
            "no_ingr INTEGER NOT NULL, " +
            "category_no INTEGER NOT NULL, " +
            "PRIMARY KEY (recipe_no , recipe_name, category_no))", 'recipe')

        #trigger = """\
        #CREATE TRIGGER recipe_number BEFORE INSERT ON recipe
        #  BEGIN
        #    UPDATE recipe SET recipe_no = recipe.ROWID WHERE recipe_no = NULL;
        #  END;
        #"""
        #self.query(trigger)
        

        # create ingredient table
        self.create_table("CREATE TABLE ingredient " + 
            "(recipe_no INTEGER NOT NULL, " + 
            "amount REAL NOT NULL, " +
            "Msre_No INTEGER NOT NULL, " +
            "NDB_No INTEGER NOT NULL)", 'ingredient')

        # create recipe category table
        self.create_load_table("CREATE TABLE category " +
            "(category_no INTEGER PRIMARY KEY NOT NULL, " +
            "category_desc TEXT NOT NULL)",
            ### Insert statement
            "INSERT INTO 'category' VALUES (?, ?)",
            'category')

        # create recipe preparation table
        self.create_table("CREATE TABLE preparation " +
            "(recipe_no INTEGER PRIMARY KEY NOT NULL, " +
            "prep_time TEXT, " +
            "prep_desc TEXT)", 'preparation')

        # create person table
        self.create_table("CREATE TABLE person " +
            "(person_no INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL," +
            "person_name TEXT, " +
            "user_name TEXT)", 'person')

        # create food_plan table
        self.create_table("CREATE TABLE food_plan " +
            "(person_no INTEGER NOT NULL, " +
            "date TEXT NOT NULL, " +
            "time TEXT NOT NULL, " +
            "amount REAL NOT NULL, " +
            "Msre_No INTEGER NOT NULL, " +
            "Ndb_No INTEGER NOT NULL)", 'food_plan')

        # create recipe_plan table
        self.create_table("CREATE TABLE recipe_plan " +
            "(person_no INTEGER NOT NULL, " +
            "date TEXT NOT NULL, " +
            "time TEXT NOT NULL, " +
            "no_portions REAL NOT NULL, " +
            "recipe_no INTEGER NOT NULL)", 'recipe_plan')

        # create nutr_goal table
        self.create_table("CREATE TABLE nutr_goal " +
            "(person_no INTEGER NOT NULL, " +
            "Nutr_No INTEGER NOT NULL, " +
            "goal_val REAL NOT NULL)", 'nutr_goal')

        self.cursor.close()
        self.cursor = self.db.cursor()
        return 1

    def curtime(self):
        return curtime()

    def curdate(self):
        return curdate()

    def query(self, sql, many=False, sql_params=None, caller=None):
        """Execute the SQL statement with given SQL parameters."""
        try:
            if sql_params:
                if many:
                    self.cursor.executemany(sql, sql_params)
                else:
                    self.cursor.execute(sql, sql_params)
            elif many:
                self.cursor.executemany(sql)
            else:
                self.cursor.execute(sql)
        except self.Error, sqlerr:
            import sys
            print 'Error :', sqlerr, '\nquery:', sql
            if caller: print 'Caller ', caller
            sys.exit()
        result = self.cursor.fetchall()
		# Convert to tuple as GNUtrition code expects MySQLdb tuple return
        self.result = tuple(result)
        self.last_query = sql
        self.last_query_params = sql_params
        self.db.commit()

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
            data = csv.reader(open(data_fn, 'r'), delimiter='^', quotechar="'")
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

if __name__ == '__main__':
    db = Database()
    #db.initialize()
