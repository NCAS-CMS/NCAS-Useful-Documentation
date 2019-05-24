# (C) British Crown Copyright 2018, Met Office.
"""
This module acts as a wrapper to MIP Convert processes, completing the
mip_convert config file templates for each job and arranging symlinks
to manage the volume of data that MIP Convert can see.
"""
import cf_units

CYLC_DATE_FORMAT = '%Y%m%dT%H%M%SZ'
LOG_DIRECTORY_PERMISSIONS = 0775  # owner & group write
MIP_CONVERT_CFG_FMT = 'mip_convert.{}.cfg'
MIP_CONVERT_DATE_FORMAT = ('{0.year:04d}-{0.month:02d}-{0.day:02d}-'
                           '{0.hour:02d}-{0.minute:02d}-{0.second:02d}')
NEMO_SUBSTREAMS = ['grid-T', 'grid-U', 'grid-V', 'grid-W', 'scalar', 'diaptr']
STREAM_FILES_PER_MONTH = {
    'ap4': 1, 'ap5': 1, 'apu': 1,  # Monthly streams
    'ap6': 3, 'ap7': 3, 'ap8': 3, 'ap9': 3,  # Daily 6hr, 3hr, 1hr
    'inm': 1, 'onm': 1,  # Seaice and Ocean monthly
    'ind': 1, 'ond': 1}  # Seaice and Ocean daily
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'
TIME_UNIT = cf_units.Unit('days since 1850-01-01', calendar='360_day')
