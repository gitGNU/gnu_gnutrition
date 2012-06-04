#!/usr/bin/env python
#
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

from os import path, rename

pfx = path.join('..', 'data')
weight_orig = path.join(pfx, 'WEIGHT.orig')
weight_out = path.join(pfx, 'WEIGHT.txt')
if not path.isfile(weight_orig):
    rename(weight_out, weight_orig)
measure = path.join(pfx, 'MEASURE.txt')

field_dict = {'NDB_No':0, 'Seq':1, 'Amount':2, 'Msre_Desc':3, 'Gm_wgt':4}
weight_fmt = "%s^%s^%s^%s^%s\n"
measure_fmt = "%s^%s\n"

measure_out = open(measure, 'w')
weight_out = open(weight_out, 'w')
weight_in = open(weight_orig, 'r')

for line in weight_in:
    field_list = line.rstrip().split('^')
    Msre_No = int(str(field_list[field_dict['NDB_No']]) + 
                  str(field_list[field_dict['Seq']]))

    weight_out.write(weight_fmt % (field_list[field_dict['NDB_No']],
                                   field_list[field_dict['Seq']],
                                   field_list[field_dict['Amount']],
                                   Msre_No,
                                   field_list[field_dict['Gm_wgt']]))


    measure_out.write(measure_fmt % (Msre_No, field_list[field_dict['Msre_Desc']]))

weight_in.close()
weight_out.close()
measure_out.close()
