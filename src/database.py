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
import install
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
        try:
            self.cursor.execute('SHOW DATABASES')
            list_db = self.cursor.fetchall()
        except:
            import sys
            import traceback
            traceback.print_exc()
            sys.exit()
#            pass

        match = 0
        for b in list_db:
            if b[0] == 'gnutr_db':
                match = 1
        if match == 1: 
            return 0

        self.query('CREATE DATABASE gnutr_db')
        self.query('USE gnutr_db')

        # Create Food Description (food_des) table.
        # Data file FOOD_DES.
        self.create_load_table("CREATE TABLE food_des " +
            "(NDB_No SMALLINT(5) UNSIGNED NOT NULL, " + 
            "FdGrp_Cd SMALLINT(4) UNSIGNED NOT NULL, " + 
            "Long_Desc CHAR(200) NOT NULL, " + 
            "Shrt_Desc CHAR(60) NOT NULL, " + 
            # Three new fields for sr24
            "ComName CHAR(100), " + 
            "ManufacName CHAR(65), " +
            "Survey CHAR(1), " +
            # end new
            "Ref_desc CHAR(135), " + 
            "Refuse SMALLINT(3), " + 
            "SciName CHAR(65), " + 
            "N_Factor FLOAT(4,2), " +
            "Pro_Factor FLOAT(4,2), " + 
            "Fat_Factor FLOAT(4,2), " + 
            "CHO_Factor FLOAT(4,2), " + 
            "INDEX (NDB_No), INDEX (FdGrp_Cd) " +
            ") ENGINE=InnoDB", 'food_des')

        # Create Food Group Description (fd_group) table.
        # Data file FD_GROUP.
        self.create_load_table("CREATE TABLE fd_group " + 
            "(FdGrp_Cd SMALLINT(4) UNSIGNED NOT NULL, " + 
            "FdGrp_Desc CHAR(60) NOT NULL, " + 
            "INDEX (FdGrp_Cd)) " +
            "ENGINE=InnoDB", 'fd_group')

        # Create Nutrient Data (nut_data) table.
        # Data file NUT_DATA
        self.create_load_table("CREATE TABLE nut_data " + 
            "(NDB_No SMALLINT(5) UNSIGNED NOT NULL, " + 
            "Nutr_No SMALLINT(3) UNSIGNED NOT NULL, " + 
            "Nutr_Val FLOAT(10,3) NOT NULL, " + 
            "Num_Data_Pts FLOAT(5,0) NOT NULL, " + 
            "Std_Error FLOAT(8,3), " + 
            "Src_Cd CHAR(2) NOT NULL, " +
            # New fields in sr24
            "Deriv_Cd CHAR(4), " +
            "Ref_NDB_No CHAR(5), " +
            "Add_Nutr_Mark CHAR(1), " +
            "Num_Studies SMALLINT(2), " +
            "Min FLOAT(10,3), " +
            "Max FLOAT(10,3), " +
            "DF SMALLINT(2), " +
            "Low_EB FLOAT(10,3), " +
            "Up_EB FLOAT(10,3), " +
            "Stat_cmt CHAR(10), " +
            "AddMod_Date CHAR(10), " +
            "CC CHAR(1), " +
            # end new fields
            "INDEX (NDB_No, Nutr_No) " +
            ") " +
            "ENGINE=InnoDB", 'nut_data')

        # Create Nutrient Definition (nutr_def table.
        # Data file NUTR_DEF
        self.create_load_table("CREATE TABLE nutr_def " + 
            "(Nutr_No SMALLINT(3) UNSIGNED NOT NULL, " + 
            "Units CHAR(7) NOT NULL, " +
            "Tagname CHAR(20), " +
            "NutrDesc CHAR(60) NOT NULL, " +
            # Two new in sr24
            "Num_Dec SMALLINT(1) NOT NULL, " +
            "SR_Order MEDIUMINT(6) NOT NULL, " +
            #
            "INDEX (Nutr_No)) " +
            "ENGINE=InnoDB", 'nutr_def')

        # Create temporary weight table.
        # Data file WEIGHT.
        self.create_load_table("CREATE TABLE weight" +
            "(NDB_No SMALLINT(5) UNSIGNED NOT NULL, " +
            # Seq == Sequence number for measure description (Msre_Desc)
            # The NDB_No for a food item will appear once for each measure
            # description. Measure descriptions are sequenced. For example:
            # NDB_No Seq Amount Msre_Desc                Gm_wgt
            # 01001   1    1     cup                       227
            # 01001   2    1     tbsp                       14.2
            # 01001   3    1     pat (1" sq, 1/3" high)      5.0
            # 01001   4    1     stick                     113
            "Seq SMALLINT(2) NOT NULL, " +
            # Amount == Unit modifier (for example, 1 in "1 cup").
            "Amount FLOAT(5,3) NOT NULL, " +
            "Msre_No MEDIUMINT(6) UNSIGNED NOT NULL, " +
            "Gm_wgt FLOAT(7,1) NOT NULL, " +
            "INDEX (NDB_No, Seq) " +
            ")ENGINE=InnoDB", 'weight')

        # create measure table
        self.create_load_table("CREATE TABLE measure " +
            "(Msre_No MEDIUMINT(6) UNSIGNED NOT NULL, " +
            "Msre_Desc CHAR(80) NOT NULL, " +
            "INDEX(Msre_No) ) " +
            "ENGINE=InnoDB", 'measure')

        # create recipe table
        self.create_table("CREATE TABLE recipe " +
            "(recipe_no MEDIUMINT(6) UNSIGNED NOT NULL AUTO_INCREMENT, " +
            "recipe_name CHAR(200) NOT NULL, " +
            "no_serv SMALLINT(4) UNSIGNED NOT NULL, " +
            "no_ingr SMALLINT(4) UNSIGNED NOT NULL, " +
            "category_no TINYINT(3) UNSIGNED NOT NULL, " +
            "PRIMARY KEY (recipe_no), " +
            "INDEX (recipe_name(20), category_no)) " +
            "ENGINE=InnoDB", 'recipe')

        # create ingredient table
        self.create_table("CREATE TABLE ingredient " + 
            "(recipe_no MEDIUMINT(6) NOT NULL, " + 
            "amount FLOAT(7,2) NOT NULL, " +
            "Msre_No MEDIUMINT(5) UNSIGNED NOT NULL, " +
            "NDB_No SMALLINT(5) UNSIGNED NOT NULL, " +
            "INDEX (recipe_no)) " +
            "ENGINE=InnoDB", 'ingredient')

        # create recipe category table
        self.create_load_table("CREATE TABLE category " +
            "(category_no TINYINT(3) UNSIGNED NOT NULL, " +
            "category_desc CHAR(40) NOT NULL, " +
            "INDEX (category_no)) " +
            "ENGINE=InnoDB", 'category')

        # create recipe preparation table
        self.create_table("CREATE TABLE preparation " +
            "(recipe_no MEDIUMINT(6) UNSIGNED NOT NULL, " +
            "prep_time CHAR(50), " +
            "prep_desc TEXT, " +
            "INDEX (recipe_no)) " +
            "ENGINE=InnoDB", 'preparation')

        # create person table
        self.create_table("CREATE TABLE person " +
            "(person_no SMALLINT(6) UNSIGNED NOT NULL AUTO_INCREMENT " +
            "PRIMARY KEY, " +
            "person_name CHAR(100), INDEX person_name (person_name(10)), " +
            "user_name CHAR(50)) " +
            "ENGINE=InnoDB", 'person')

        # create food_plan table
        self.create_table("CREATE TABLE food_plan " +
            "(person_no SMALLINT(6) UNSIGNED NOT NULL, " +
            "date DATE NOT NULL, " +
            "time TIME NOT NULL, " +
            "amount FLOAT(7,2) NOT NULL, " +
            "Msre_No MEDIUMINT(6) NOT NULL, " +
            "Ndb_No SMALLINT(5) UNSIGNED NOT NULL) " +
            "ENGINE=InnoDB", 'food_plan')

        # create recipe_plan table
        self.create_table("CREATE TABLE recipe_plan " +
            "(person_no SMALLINT(6) UNSIGNED NOT NULL, " +
            "date DATE NOT NULL, " +
            "time TIME NOT NULL, " +
            "no_portions FLOAT(7,2) NOT NULL, " +
            "recipe_no MEDIUMINT(6) UNSIGNED NOT NULL) " +
            "ENGINE=InnoDB", 'recipe_plan')

        # create nutr_goal table
        self.create_table("CREATE TABLE nutr_goal " +
            "(person_no SMALLINT(6) UNSIGNED NOT NULL, " +
            "Nutr_No SMALLINT(3) UNSIGNED NOT NULL, " +
            "goal_val FLOAT(11,4) NOT NULL) " +
            "ENGINE=InnoDB", 'nutr_goal')
        self.cursor.close()
        self.cursor = self.db.cursor()
        return 1

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
        from os import path
        self.create_table(query, filename)
        fn = path.join(install.dir,'data',filename.upper() + '.txt')
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
