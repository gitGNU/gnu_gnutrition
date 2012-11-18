"""Default values related to gnutrition version and program default values."""
#  GNUtrition - a nutrition and diet analysis program.
#  Copyright(C) 2000-2002 Edgar Denny (edenny@skyweb.net)
#  Copyright (C) 2012 Free Software Foundation, Inc.
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

# Logging defaults
LOGGING = 'on'
LOG_LEVEL = 'warn'  # off, debug, info, warn, error, critical 
LOG_ROTATE = 3      # New one started when LOG_MAX_SZ is reached.
LOG_MAX_SZ = 50000

# This needs to be added to install process, somthing like:
# configure --disable-version-check
CHECK_DISABLED = False
# Next two can be changed by user
CHECK_VERSION = True
CHECK_INTERVAL = 604800   # 60*60*24*7 (one week)

# This file has version information for both the latest application version
# and the current USDA Standard Reference Database version.
BASE_URL = "http://www.gnu.org/software/gnutrition/"
LATEST_VERSION = BASE_URL + "version"

PLAN = 0
RECIPE = 1
FOOD = 2

START = 0
END = 1

GRAPHICAL = 0
DIALOG = 1
