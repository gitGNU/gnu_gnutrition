#/bin/sh
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
