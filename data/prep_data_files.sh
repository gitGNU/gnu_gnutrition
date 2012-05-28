#/bin/sh
#
# Copyright (C) 2012 Free Software Foundation, Inc.
# 
# This file is part of GNUtrition.
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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# 1. substitute any DOS type control characters with "\n"
# 2. remove any "~"
# The field separator is kept as "^".
# This puts the files in the correct state for the database.

# Called as  ./prep_data_files.sh *.txt

while [ $# -gt 0 ]; do
	tr -s "[\015\032]" "\n" < ${1} | tr -d "~" > ${1}.tmp
	mv ${1}.tmp ${1}
	shift 1
done
touch .data_prepped
