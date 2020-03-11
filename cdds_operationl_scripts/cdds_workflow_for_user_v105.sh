############### user variables: edit as needed ############
export CDDS_DIR="/home/users/valeriu/cdds_example_Sept2019"  # needs to be exported for Python env
export FILEPATHSTYPE="METOFFICE"  # or ARCHER
REQUEST_JSON=req.json


################ end user edits ###########################
#######################################################
############### system: do not edit #######################
echo "####################### Starting CDDS ##################"
echo "Main directory for work: CDDS_DIR:"
echo $CDDS_DIR
echo "Request file:"
echo $REQUEST_JSON

# system variables; to be modified only by admin
echo "Sourcing environment..."
ENV_LOC=/home/users/valeriu/cdds_example_Sept2019/
ENV_FILE=setup_cdds_env.sh
source $ENV_LOC/$ENV_FILE

# parse request json for system variables
MIP=$(sed -e 's/^"//' -e 's/"$//' <<<"$(jq '.mip' $REQUEST_JSON)")
MIPERA=$(sed -e 's/^"//' -e 's/"$//' <<<"$(jq '.mip_era' $REQUEST_JSON)")
MODELID=$(sed -e 's/^"//' -e 's/"$//' <<<"$(jq '.model_id' $REQUEST_JSON)")
REQUESTID=$(sed -e 's/^"//' -e 's/"$//' <<<"$(jq '.request_id' $REQUEST_JSON)")
PACKAGE=$(sed -e 's/^"//' -e 's/"$//' <<<"$(jq '.package' $REQUEST_JSON)")
CONFIGVERSION=$(sed -e 's/^"//' -e 's/"$//' <<<"$(jq '.config_version' $REQUEST_JSON)")


# initialize dirs
echo "Exporting temp dir TMPDIR=$CDDS_DIR/tmp ..."
export TMPDIR=$CDDS_DIR/tmp
mkdir -p $TMPDIR
mkdir -p $CDDS_DIR

# verify executables
echo "####################### Verifying CDDS components ##################"
which create_cdds_directory_structure
create_cdds_directory_structure --help
which prepare_generate_variable_list
prepare_generate_variable_list --help
which cdds_configure
cdds_configure --help
which cdds_convert
cdds_convert --help
which mip_convert
mip_convert --help
which rose

# run steps
echo "####################### Changing CMIP6.cfg ##################"
# change the roots to output dirs
USER_DATAROOT=$CDDS_DIR/cdds_data
USER_PROC=$CDDS_DIR/cdds_proc

# run the CDDS pipeline stages
echo "####################### Running CDDS pipeline stages ##################"
# create IO structure
echo "Creating CDDS directory structure..."
LOGFILE=$CDDS_DIR/create_cdds_directory_structure.log
if test -f "$LOGFILE"; then
    echo "$LOGFILE exists, removing it to be replaced with current run."
    rm $LOGFILE
fi
create_cdds_directory_structure -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON
ret=$?
if [ $ret -ne 0 ]; then
     "Code has crashed with non-zero status. Check $LOGFILE if available"
     return
fi
if grep Traceback $LOGFILE; then
    echo "Found Python Traceback in $LOGFILE. Stopping."
    return
fi

# create variable list
echo "Preparing variables list..."
LOGFILE=$CDDS_DIR/cdds_prepare_generate.log
if test -f "$LOGFILE"; then
    echo "$LOGFILE exists, removing it to be replaced with current run."
    rm $LOGFILE
fi
prepare_generate_variable_list -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON --output_dir $CDDS_DIR/cdds_proc/$MIPERA/$MIP/$REQUESTID/$PACKAGE/prepare/
ret=$?
if [ $ret -ne 0 ]; then
     "Code has crashed with non-zero status. Check $LOGFILE if available"
     return
fi
echo "Verifying prepare variables activity log..."
if grep CRITICAL $LOGFILE; then
    echo "Found Python Traceback in $LOGFILE. Stopping."
    return
fi
if grep Traceback $LOGFILE; then
    echo "Found Python Traceback in $LOGFILE. Stopping."
    return
fi

# configure
echo "Preparing CDDS convert configuration files"
LOGFILE=$CDDS_DIR/cdds_proc/$MIPERA/$MIP/$REQUESTID/$PACKAGE/configure/log/cdds_configure.log
if test -f "$LOGFILE"; then
    echo "$LOGFILE exists, removing it to be replaced with current run."
    rm $LOGFILE
fi
cdds_configure -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON -m -p -t
ret=$?
if [ $ret -ne 0 ]; then
     "Code has crashed with non-zero status. Check $LOGFILE if available"
     return
fi
echo "Verifying prepare variables activity log..."
if grep CRITICAL $LOGFILE; then
    echo "Found Python Traceback in $LOGFILE. Stopping."
    return
fi
if grep Traceback $LOGFILE; then
    echo "Found Python Traceback in $LOGFILE. Stopping."
    return
fi

# create the setup_env_for_devel file
echo "Creating setup_env_for_devel"
cp $ENV_LOC/$ENV_FILE setup_env_for_devel
export MIPC_PYTHONPATH=$CDDS_DIR/cdds_proc/$MIPERA/$MIP/$REQUESTID/$PACKAGE/convert/u-ak283_JSON/app/mip_convert/wrapper
STR_PYTHONPTH='$PYTHONPATH'
echo "export PYTHONPATH=$STR_PYTHONPTH:$MIPC_PYTHONPATH" >> setup_env_for_devel

# run convert
echo "Running CDDS conversions"
cdds_convert -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON
