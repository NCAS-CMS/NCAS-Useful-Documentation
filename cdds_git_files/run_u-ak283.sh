# from source for inm
#rose suite-run -C /home/users/valeriu/cdds_test_May2019/cdds-example-1/cdds/proc/CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1-monthly/convert/u-ak283_JSON --no-gcontrol -v --name=cdds_UKESM1-0-LL_piControl_r1i1p1f2_inm --opt-conf-key=inm

# from source for ap4
#rose suite-run -C /home/users/valeriu/cdds_files_May2019/cdds/proc/CMIP6/CMIP/UKESM1-0-LL_piControl_r1i1p1f2/round-1-monthly/convert/u-ak283_JSON --no-gcontrol -v --name=cdds_UKESM1-0-LL_piControl_r1i1p1f2_ap4 --opt-conf-key=ap4

# from test base for ap4
#rose suite-run -C /home/users/valeriu/cdds_files_May2019/u-ak283_JSON --no-gcontrol -v --name=local_test --opt-conf-key=ap4

# run the wip suite
rose suite-run -C /home/users/valeriu/cdds_files_May2019/u-ak283_JSON_wip --no-gcontrol -v --name=local_test --opt-conf-key=ap4
