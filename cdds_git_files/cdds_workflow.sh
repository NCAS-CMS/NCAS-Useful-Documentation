# source environment
source /home/users/valeriu/cdds_files_May2019/cdds_environment.sh
# create IO structure
create_cdds_directory_structure -c /home/users/valeriu/cdds_files_May2019 /home/users/valeriu/cdds_files_May2019/piControl_request.json
# create variable list
prepare_generate_variable_list -c /home/users/valeriu/cdds_files_May2019 /home/users/valeriu/cdds_files_May2019/piControl_request.json
cp /home/users/valeriu/cdds_files_May2019/CMIP6_CMIP_piControl_UKESM1-0-LL.json /home/users/valeriu/cdds_files_May2019/cdds/proc/CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1-monthly/prepare/
# configure
cdds_configure -c /home/users/valeriu/cdds_files_May2019 /home/users/valeriu/cdds_files_May2019/piControl_request.json -m -p -t
# convert
export CDDS_DIR=/home/users/valeriu/cdds_files_May2019
export TMPDIR=/home/users/valeriu/cdds_files_May2019/tmp
cdds_convert -c /home/users/valeriu/cdds_files_May2019 /home/users/valeriu/cdds_files_May2019/piControl_request.json
