# Version cdds=1.2.2
############### user variables: edit as needed ############
# use a fast filesystem eg /home/users
export CDDS_DIR="/home/users/valeriu/cdds133_example"  # runtime files
export FILEPATHSTYPE="ARCHER"  # "METOFFICE" or "ARCHER"
export DATAREQUESTVERSION="01.00.29"
REQUEST_JSON=FAFMIP-faf-heat.json
################ end user edits ###########################

############### system: do not edit #######################
USER_PROC=$CDDS_DIR/cdds_proc
USER_DATAROOT=$CDDS_DIR/cdds_data
export DATAREQUESTDIR="/gws/smf/j04/cmip6_prep/cdds-env/etc-from-mohc/data_requests/CMIP6" # stable for Jasmin
############################################################

# print some pointers
echo "####################### Starting CDDS ##################"
echo "Main directory for work: CDDS_DIR:"
echo $CDDS_DIR
echo "Request file:"
echo $REQUEST_JSON
echo "CDDS processing directory"
echo $USER_PROC
echo "CDDS data directory"
echo $USER_DATAROOT
echo "Data request directory"
echo $DATAREQUESTDIR

# environment sourcing
echo "Sourcing CDDS software environment..."
ENV_FILE=/gws/smf/j04/cmip6_prep/cdds-env/setup_cdds_env_cdds133.sh
source $ENV_FILE
echo "Sourced CDDS software environment file:"
echo $ENV_FILE

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
create_cdds_directory_structure --version
which prepare_generate_variable_list
prepare_generate_variable_list --version
# v105+
# which cdds_configure
# cdds_configure --version
which generate_user_config_files
generate_user_config_files --version
which cdds_convert
cdds_convert --version
which mip_convert
mip_convert --version
which rose

# run the CDDS pipeline stages
echo "####################### Running CDDS pipeline stages ##################"

# create IO structure
echo "Creating CDDS directory structure..."
LOGFILE=$CDDS_DIR/*create_cdds_directory_structure*.log*
if test -f "$LOGFILE"; then
    echo "$LOGFILE exists, removing it to be replaced with current run."
    rm $LOGFILE
fi
# v105+
# create_cdds_directory_structure -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON
create_cdds_directory_structure -c $USER_PROC -t $USER_DATAROOT $REQUEST_JSON
ret=$?
if [ $ret -ne 0 ]; then
     "Code has crashed with non-zero status. Check $LOGFILE if available"
     return
fi
if grep Traceback $LOGFILE; then
    echo "Found Python Traceback in $LOGFILE. Stopping."
    return
fi

# run prepare to create variable list
echo "Preparing variables list..."
LOGFILE=$CDDS_DIR/*prepare_generate_variable_list*.log*
if test -f "$LOGFILE"; then
    echo "$LOGFILE exists, removing it to be replaced with current run."
    rm $LOGFILE
fi
# v105+
# prepare_generate_variable_list -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON --output_dir $CDDS_DIR/cdds_proc/$MIPERA/$MIP/$REQUESTID/$PACKAGE/prepare/
# NOTE: could add -m $MIP but this was suggested to be taken off in https://github.com/cedadev/jasmin-cdds/issues/34
prepare_generate_variable_list -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON -b $DATAREQUESTDIR -d $DATAREQUESTVERSION --output_dir $USER_PROC/$MIPERA/$MIP/$REQUESTID/$PACKAGE/prepare/
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

# run configure
echo "Preparing CDDS convert configuration files"
LOGFILE=$CDDS_DIR/cdds_proc/$MIPERA/$MIP/$REQUESTID/$PACKAGE/configure/log/*cdds_configure*.log*
if test -f "$LOGFILE"; then
    echo "$LOGFILE exists, removing it to be replaced with current run."
    rm $LOGFILE
fi
# v105+
# cdds_configure -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON -m -p -t
generate_user_config_files -c $USER_PROC $CDDS_DIR/$REQUEST_JSON -m -p -d $DATAREQUESTVERSION -t $USER_DATAROOT
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
echo "Copying setup_env_for_devel"
cp $ENV_FILE setup_env_for_devel

# run convert
echo "Running CDDS conversions"
# v105+
# cdds_convert -c $CDDS_DIR $CDDS_DIR/$REQUEST_JSON
# Run only when all else has finished fine
# cdds_convert -c $USER_PROC $CDDS_DIR/$REQUEST_JSON -t $USER_DATAROOT

# run quality check (qc)
# Run this only when all the conversions and concatenations have finished without errors
# qc_run_and_report $CDDS_DIR/$REQUEST_JSON -c $USER_PROC -t $USER_DATAROOT -p
