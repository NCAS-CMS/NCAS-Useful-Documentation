# (C) British Crown Copyright 2017-2018, Met Office.
"""
Routines to perform actions such as running mip_convert or managing the
log files
"""
import glob
import logging
import os
import shutil
import subprocess

from mip_convert_wrapper import LOG_DIRECTORY_PERMISSIONS
from mip_convert_wrapper.common import print_env, setup_logger


def manage_logs(stream, component, mip_convert_config_dir,
                cylc_task_cycle_point):
    """
    Create the logs directories under
    mip_convert_config_dir/log/stream_component/date/ and move logs to
    them.

    Parameters
    ----------
    stream : str
        Stream to manage logs for.
    component : str
        Component to manage logs for.
    mip_convert_config_dir : str
        Directory containing MIP Convert config files to be managed.
    cylc_task_cycle_point : str
        Cylc task cycle point (format YYYYMMDDTHHMMZ) to use as date
        component of log directory structure.
    """
    logger = logging.getLogger(__name__)
    setup_logger(logger)
    logger.info('Managing logs')
    # suffix is a variable used in the suite.rc that is a useful shorthand.
    suffix = '_'.join([stream, component])
    dir_stem = os.path.join(mip_convert_config_dir, 'log',
                            suffix, cylc_task_cycle_point)
    work = [('cmor_logs', 'cmor*.log'),
            ('mip_convert_cfgs', 'mip_convert.*.cfg'),
            ('mip_convert_logs', 'mip_convert*.log')]
    for dir_name, file_pattern in work:
        destination = os.path.join(dir_stem, dir_name)
        if os.path.exists(destination):
            if os.path.isdir(destination):
                logger.info('Log directory "{}" already exists.'
                            ''.format(destination))
            else:
                raise RuntimeError('Expected "{}" to be a directory.'
                                   ''.format(destination))
        else:
            logger.info('Making log directory "{}"'.format(destination))
            os.makedirs(destination, LOG_DIRECTORY_PERMISSIONS)
            os.chmod(destination, LOG_DIRECTORY_PERMISSIONS)
        # Note that we are already in the working directory where MIP Convert
        # is run and as such all the log files are in the current working
        # directory.
        files_to_archive = glob.glob(file_pattern)
        for file_to_archive in files_to_archive:
            return_code = subprocess.call(['gzip', file_to_archive])
            if return_code > 0:
                logger.warning('Failed to gzip "{}".'.format(file_to_archive))
            else:
                file_to_archive = '{}.gz'.format(file_to_archive)
            dest_file_name = os.path.join(destination, file_to_archive)
            if os.path.exists(dest_file_name):
                continue
            logger.info('Archiving "{}" to "{}.gz"'.format(files_to_archive,
                                                           dest_file_name))
            shutil.copy(file_to_archive, dest_file_name)


def run_mip_convert(stream, dummy_run, timestamp):
    """
    Run MIP Convert, or perform dummy_run if specified, and update logs.

    Parameters
    ----------
    stream : str
        Stream to be processed
    dummy_run : bool
        Print environment rather than run MIP Convert. Useful for
        development and debugging.
    timestamp : str
        timestamp to use in log and config file names.

    Returns
    -------
    int
        Return code of the mip_convert process.
    """
    mip_convert_log = 'mip_convert.{}.log'.format(timestamp)
    mip_convert_cfg = 'mip_convert.{}.cfg'.format(timestamp)
    logger = logging.getLogger(__name__)
    setup_logger(logger)
    logger.info('Running mip_convert')
    logger.info('Working directory: {}'.format(os.getcwd()))
    logger.info('Writing to mip_convert log file: {}'.format(mip_convert_log))

    cmd = ('/usr/bin/time mip_convert {} -a -s {} -l {}'
           '').format(mip_convert_cfg, stream, mip_convert_log)
    logger.info('Command to execute: {}'.format(cmd))
    if dummy_run:
        logger.info('Performing dummy run')
        logger.info(print_env())
        return 0

    logger.info('Launching subprocess')
    mip_convert_proc = subprocess.Popen(cmd.split(), env=os.environ.copy(),
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
    output, error = mip_convert_proc.communicate()
    return_code = mip_convert_proc.returncode
    logger.info('============ STDOUT ============')
    logger.info(output)
    logger.info('========== STDOUT END ==========')
    logger.info('============ STDERR ============')
    logger.info(error)
    logger.info('========== STDERR END ==========')
    if return_code != 0:
        logger.critical('Command failed with return code {}'
                        ''.format(return_code))
    return return_code


def manage_critical_issues(exit_code, mip_convert_config_dir, timestamp,
                           fields_to_log=None):
    """
    Identify critical issues logged by MIP Convert and copy them to a
    central log file so that users can keep an eye on them.

    Parameters
    ----------
    exit_code : int
        Exit code returned by MIP Convert.
    mip_convert_config_dir : str
        Name of directory containing MIP Convert config files.
    timestamp : str
        Timestamp string used when creating config/log file names.
    fields_to_log : list, optional
        Information to insert into the critical issues file along
        with the CRITICAL log messages.

    Returns
    -------
    : int
        Exit code to be ultimately returned by sys.exit.
    """
    if fields_to_log is None:
        fields_to_log = []
    logger = logging.getLogger(__name__)
    critical_issues_file = os.path.join(mip_convert_config_dir, 'log',
                                        'critical_issues.log')
    mip_convert_log = 'mip_convert.{}.log'.format(timestamp)
    logger.debug('Searching "{}" for CRITICAL messages'
                 ''.format(mip_convert_log))
    critical_issues_list = []
    with open(mip_convert_log) as log_file_handle:
        for line in log_file_handle.readlines():
            if 'CRITICAL' in line:
                critical_issues_list.append(line.strip())
    # Just in case an error code is raised for a separate reason;
    if not critical_issues_list:
        logger.debug('No CRITICAL messages found')
        return exit_code

    with open(critical_issues_file, 'a') as critical_issues_log:
        for issue in critical_issues_list:
            line = '|'.join(fields_to_log + [mip_convert_log, issue])
            critical_issues_log.write(line + '\n')
    logger.info('Wrote "{}" critical issues to log file "{}"'.format(
        len(critical_issues_list), critical_issues_file))
    return 0
