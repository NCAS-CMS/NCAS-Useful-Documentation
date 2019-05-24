# (C) British Crown Copyright 2017-2018, Met Office.
"""
Command line routines for wrapping mip_convert
"""

from datetime import datetime
import logging
import os
import sys
import shutil

from mip_convert_wrapper import TIMESTAMP_FORMAT
from mip_convert_wrapper.config_updater import (
    calculate_mip_convert_run_bounds, setup_cfg_file)
from mip_convert_wrapper.common import print_env, setup_logger
from mip_convert_wrapper.file_management import (link_data,
                                                 get_all_files,
                                                 get_file_paths,
                                                 copy_to_staging_dir)
from mip_convert_wrapper.actions import (
    run_mip_convert, manage_logs, manage_critical_issues)


def main():
    """
    Retrieve the required parameters from environment variables, set up
    the mip_convert.cfg config file and run mip_convert.
    """
    # Configure logger
    # Could this be replaced with hadsdk.common.configure_logger?
    # May require changes to configure_logger as this only logs to stdout
    logger = logging.getLogger(__name__)
    setup_logger(logger)

    # Log basic info
    logger.info('MIP convert wrapper starting')
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    logger.info('Using timestamp "{}"'.format(timestamp))
    logger.info('Python executable: {}'.format(sys.executable))

    # Collect required environment variables
    component = os.environ['COMPONENT']
    cycle_duration = os.environ['CYCLE_DURATION']
    cylc_task_name = os.environ['CYLC_TASK_NAME']
    cylc_task_try = os.environ['CYLC_TASK_TRY_NUMBER']
    cylc_task_work_dir = os.environ['CYLC_TASK_WORK_DIR']
    cylc_task_cycle_point = os.environ['CYLC_TASK_CYCLE_POINT']
    dummy_run = os.environ['DUMMY_RUN'] == 'TRUE'
    end_year = os.environ['END_YEAR']
    input_dir = os.environ['INPUT_DIR']
    mip_convert_config_dir = os.environ['MIP_CONVERT_CONFIG_DIR']
    cdds_convert_proc_dir = os.environ['CDDS_CONVERT_PROC_DIR']
    output_dir = os.environ['OUTPUT_DIR']
    stream = os.environ['STREAM']
    stream_time_overrides = os.environ['STREAM_TIME_OVERRIDES']
    suite_name = os.environ['SUITE_NAME']
    staging_dir = os.environ.get('STAGING_DIR', '')

    # Calculate start and end dates for this step
    # Final date is the 1st of January in the year after final_year (the final
    # year to be processed).
    end_dt = datetime(int(end_year) + 1, 1, 1)
    start_date, end_date = calculate_mip_convert_run_bounds(
        cylc_task_cycle_point, cycle_duration, end_dt,
        stream_time_overrides)

    # Identify whether there is any work to be done in this job step.
    job_days = (end_date - start_date).days
    if job_days < 0:
        logger.warning('Job end date before start date\n'
                       'start date: {}\n'
                       'end date: {}\n'.format(start_date, end_date))
    if job_days <= 0:
        logger.info('No work for this job step. Exiting with code 0')
        sys.exit(0)

    if staging_dir:
        input_staging_dir = os.path.join(staging_dir, 'input')
        work_dir = input_staging_dir
        output_staging_dir = os.path.join(staging_dir, 'output')
        mip_convert_output_dir = output_staging_dir
        logger.info('Running mip convert using staging directory:\n{0}\n'
                    ''.format(staging_dir))
    else:
        work_dir = cylc_task_work_dir
        mip_convert_output_dir = output_dir
        logger.info('Running mip convert using symlinking in work '
                    'directory:\n{0}\n'.format(work_dir))

    # get all filenames
    expected_files  = get_all_files(suite_name,
                                    stream,
                                    start_date,
                                    end_date,
                                    input_dir,
                                    work_dir,
                                    )
    num_files_processed = 0
    for _, _, target_filename in expected_files:
        (expected_file,
         expected_dir,
         new_input_dir) = get_file_paths(target_filename,
                                         suite_name,
                                         stream, input_dir,
                                         work_dir)
        if staging_dir:
            if expected_file:
                copy_to_staging_dir(expected_file,
                                    expected_dir, new_input_dir, )
                num_files_processed += 1
        else:
            if expected_file:
                # Set up symlinks to the data
                try:
                    link_data(expected_file,
                              expected_dir,
                              new_input_dir,
                              )
                    num_files_processed += 1
                except Exception as error:
                    logger.critical('link_data failed with error: "{}"'.format(error))
                    logger.info(print_env())
                    raise error
    logger.info("Number of processed files: {}".format(num_files_processed))

    # If nothing linked then log a critical failure and exit
    if num_files_processed == 0:
        logger.critical('No files processed to for this job step, but work is '
                        'still expected. Exiting with error code 1')
        sys.exit(1)

    # Write out config file
    try:
        setup_cfg_file(work_dir,
                       mip_convert_output_dir,
                       mip_convert_config_dir,
                       component,
                       start_date,
                       end_date,
                       timestamp)
    except Exception as error:
        logger.critical('Setup_cfg_file failed with error: "{}"'.format(error))
        logger.info(print_env())
        raise error

    # Run mip convert
    exit_code = run_mip_convert(stream, dummy_run, timestamp)

    # If exit code is 2 then MIP Convert has run, but hasn't been able to do
    # everything asked of it. The CDDS approach to this is to continue on
    # but log the failure in a critical issues log.
    if exit_code == 2:
        exit_code = manage_critical_issues(
            exit_code, cdds_convert_proc_dir, timestamp,
            fields_to_log=[cylc_task_name, cylc_task_cycle_point,
                           cylc_task_try])

    # move file from staging directory to output directory
    if staging_dir:
        component_dir_list = os.listdir(output_staging_dir)
        for dir1 in component_dir_list:
            full_comp_dir_path = os.path.join(output_staging_dir, dir1)
            out_comp_dir_path = os.path.join(output_dir, dir1)
            if os.path.isdir(out_comp_dir_path):
                logger.info('deleting old directory output directory: {0}'
                            ''.format(out_comp_dir_path))
                shutil.rmtree(out_comp_dir_path)
            logger.info('copying component directory from {src} to {dest}'
                        ''.format(src=full_comp_dir_path,
                                  dest=out_comp_dir_path))
            shutil.copytree(full_comp_dir_path,
                            out_comp_dir_path)

    # Tidy up the log files even if this task fails.
    manage_logs(stream, component, cdds_convert_proc_dir,
                cylc_task_cycle_point)
    # And we are done.
    logger.critical('Exiting with code {}'.format(exit_code))
    sys.exit(exit_code)
