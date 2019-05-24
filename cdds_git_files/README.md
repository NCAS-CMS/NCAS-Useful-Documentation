Environment
============
```
create --name cdds --file conda_spec_file.txt
```
source activate cdds
python: Python 2.7.15
get the MO env in:
```
export PATH=/apps/contrib/metomi/bin:$PATH
```
install from pip what conda didn't:
```
pip install dreqpy
```
Jinja2 now needs to be installed
================================
```
conda install jinja2
```

Workflow
========
Follow workflow from `cdds_workflow.sh` with setps below.

Configuration
================
Location to CMIP6.cfg defaults to install dir eg
```
/home/users/valeriu/miniconda2Dec2018/envs/cdds/lib/python2.7/site-packages/hadsdk-1.0.5-py2.7.egg/hadsdk/general_config/CMIP6/v1.0.1/general/CMIP6.cfg
```

This is seriously like treasure hunting!

Running with -c option and putting the cfg in:
```
/home/users/valeriu/cdds_files_May2019/CMIP6/v1.0.5/general
```

Run command
-----------
```
create_cdds_directory_structure -c /home/users/valeriu/cdds_files_May2019 /home/users/valeriu/cdds_files_May2019/piControl_request.json
```

Prepare
==========

2.1 dreq docs hardcoded path
----------------------------
```
/home/users/valeriu/miniconda2Dec2018/envs/cdds/lib/python2.7/site-packages/hadsdk-1.0.5-py2.7.egg/hadsdk/data_request_interface/load.py
DATA_REQUEST_BASE_DIR = '/home/h03/cdds/etc/data_requests/CMIP6'
hardcoded; also hardcoded is the follow-up structure:
IOError: File or directory does not exist: "/home/h03/cdds/etc/data_requests/CMIP6/01.00.29/dreqPy/docs"
```

Replace with 
```
DATA_REQUEST_BASE_DIR = '/home/users/valeriu/cdds_files_May2019/data_requests/CMIP6'
```

2.2 data request mismatch
--------------------------
Data request for
UKESM1-0-LL = 01.00.17 (see CMIP6.cfg)
```
[external_versions]
data_request = 01.00.17  # VP: this should be overwritten by version in [data_request_version_for_model_setup]
CMOR = 3.4.0
```

Download the requested version:
```
svn checkout http://proj.badc.rl.ac.uk/svn/exarch/CMIP6dreq/tags/01.00.17/dreqPy/docs
```
in 
```
/home/users/valeriu/cdds_files_May2019/data_requests/CMIP6/01.00.17/dreqPy
```

Run command
-----------
```
prepare_generate_variable_list -c /home/users/valeriu/cdds_files_May2019 /home/users/valeriu/cdds_files_May2019/piControl_request.json
```
NOTE: use -p to prepare command to specify the targer write dir
(see next error from configure)

Configure
=============
```
IOError: [Errno 2] No such file or directory: '/home/users/valeriu/cdds_files_May2019/cdds/proc/CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1-monthly/prepare/CMIP6_CMIP_piControl_UKESM1-0-LL.json'
```

prepare creates the file in the main dir:

```
/home/users/valeriu/cdds_files_May2019/
```
Solution from Piotr: use -p to prepare command to specify the targer write dir

Run command
-----------
```
cdds_configure -c /home/users/valeriu/cdds_files_May2019 /home/users/valeriu/cdds_files_May2019/piControl_request.json -m -p -t
```
Convert
===========

4.1. Extra environment variables
---------------------------------
```
export CDDS_DIR=/home/users/valeriu/cdds_files_May2019
export TMPDIR=/home/users/valeriu/cdds_files_May2019/tmp --> this is not needed anymore if not using copying (STAGING_DIR)
```

4.2 Symlink data
------------------
Only for a local test on Jasmin, not for production
symlink data:
```
ln -s /group_workspaces/jasmin2/ukesm/willie/u-bd204/* /home/users/valeriu/cdds_files_May2019/cdds_data/CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/round-1-monthly/input/u-bd204
```

Run command
------------
```
export CDDS_DIR=/home/users/valeriu/cdds_files_May2019
export TMPDIR=/home/users/valeriu/cdds_files_May2019/tmp --> this is not needed anymore if not using copying (STAGING_DIR)
cdds_convert -c /home/users/valeriu/cdds_files_May2019 /home/users/valeriu/cdds_files_May2019/piControl_request.json
```

5 Convert Suite modifications
==============================
5.1 Use of u-bd204
------------------
Suite:
```
cdds/proc/CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1-monthly/convert/u-ak283_JSON/rose-suite.conf
```
Data from Willy's u-bd204 is 1960-1990 so adjust `START_YEAR` and `END_YEAR`

change SPICE -> LOTUS for inheritance for suite.rc

5.2 Setup env in `app/mip_convert`
---------------------------------
`setup_env_for_cdds` is a pain in the arse - why still needed?
```
job.err: /bin/sh: ~cdds/bin/setup_env_for_cdds: No such file or directory
```
classic u-ak283 `mip_convert` error
sourced from: `cdds/proc/CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1-monthly/convert/u-ak283_JSON/app/mip_convert/rose-app.conf`

replace in rose-app.conf:
```
setup=/home/users/valeriu/cdds_files_May2019/setup_env_for_cdds (or _local for in-dir run)
```

and populate that file with:

```
export PATH=/home/users/valeriu/miniconda2Dec2018/bin:$PATH
export PYTHONPATH=$PYTHONPATH:/home/users/valeriu/cdds_files_May2019/cdds/proc/CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1-monthly/convert/u-ak283_JSON/app/mip_convert/wrapper
```

Run command
-----------
for a local run of a local `u-ak283_JSON` for ap4 only:
```
rose suite-run -C /home/users/valeriu/cdds_files_May2019/u-ak283_JSON --no-gcontrol -v --name=local_test --opt-conf-key=ap4
```
NOTE: cmorized output will be written in eg `$CDDS_DIR/cdds_data/CMIP6/CMIP/UKESM1-0-LL/piControl/r1i1p1f2/round-1-monthly/output/`
and that is a LOT of output, need dedicated location on a GWS

6 Mip convert and staging area
===============================
Staging directory for copying is useless - symlinking option does the job faster and
at no extra disk space. `ak283_JSON` comes by default with `STAGING_DIR="$TMPDIR"` - how to turn it off automatically?
Setting it to ='' manually in rose-suite.conf will do but not automatically. Even if completely
removed from conf it's still set in suite.rc as `BASE_CONCAT`

Solution found!
---------------
in suite.rc:
```
        {% if USE_LOCAL_STORAGE %}
                STAGING_DIR=$TMPDIR
```
so in rose-suite.conf: `USE_LOCAL_STORAGE = false`

File finders
-------------
File finders funcs don't work unless on MO dir tree: I wrote universal ones:
New code available: `/home/users/valeriu/cdds_files_May2019/mip_convert_app_changeRequest`
or here on gitHub
 - `command_line.py`
 - `file_management.py`

7 Orography, levels and ancil files
===================================
Need them on Jasmin eg

`ERROR: File "/project/cdds/etc/vertical_coordinates/atmosphere_theta_levels_85.txt" does not exist`

Temporary solution
-------------------
As of May 23 2019, Matt has put all the files on `/gws/nopw/j04/cmip6_prep_vol1/cache/msm/CDDS`
