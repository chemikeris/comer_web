#! /bin/bash

set -o nounset
set -o errexit

usage="$0 pdb_update_rsync_log"

if [ $# -eq 0 ] || [[ "$1" == '-h' ]] || [[ "$1" == '--help' ]]; then
    echo "$usage"
    exit
fi

rsync_log_file=$(realpath "$1")

workdir=$(mktemp -d)
cd $workdir

wget https://files.wwpdb.org/pub/pdb/derived_data/pdb_seqres.txt
cat $rsync_log_file | grep 'cif.gz$' | grep -v deleting | awk -F'/' '{print $2}' | awk -F'.' '{print $1}' > pdb_ids.txt
cat pdb_seqres.txt | grep -f pdb_ids.txt

rm -rf $workdir
