# (C) British Crown Copyright 2017-2018, Met Office.
"""
Routines for generating links to data files in order to restrict the
volume of data that MIP Convert can see and attempt to read
"""
import calendar
import shutil
from datetime import datetime
import itertools
import logging
import os
import glob

from mip_convert_wrapper import (
    TIME_UNIT, STREAM_FILES_PER_MONTH, NEMO_SUBSTREAMS)
from mip_convert_wrapper.common import setup_logger


def get_all_files(suite_name, stream, start_date, end_date, input_dir, work_dir):
    """
    Creates a list of paths to current input directory, directory for symlinks
    or copies of the files, and a list of the files name thatwill be input
    to this batch of processing.

    Parameters
    ----------
    suite_name: str
        The name of the suite that the ran the model
    stream: str
        The model output stream to be processed
    start_date: str
        The start date of the data to be processed
    end_date: str
        The end date of the data to be processed
    input_dir: str
        The base directory of the current file directory
            (this excludes the suite name and the stream name)
    work_dir: str
        The base firectory for copying or symlinking

    Returns
    -------
    expected_files: list
    expected_files - list of expected input files for this processing

    """
    runid = suite_name[-5:]
    stream_prefix = stream[:2]  # `ap`, `in` or `on`
    if stream_prefix not in ['ap', 'in', 'on']:
        raise RuntimeError('Stream "{}" not recognised'.format(stream))

    # Identify files that are to be expected
    expected_files_generator = {
        'ap': _expected_ap, 'in': _expected_in, 'on': _expected_on}
    expected_files = expected_files_generator[stream_prefix](
        runid, stream, start_date, end_date)

    return expected_files


def get_file_paths(target_filename, suite_name, stream, input_dir, work_dir):
    """
    Find files in a generic input directory tree.

    Creates full path to data files that exist in an arbitrary directory tree.
    The input directory must be of type $INPUT/$SUITENAME but inside it can
    be of Met Office type (stream/file) or it can be of Jasmin type
    (YYYYMMDDT0000Z/files).

    Parameters
    ----------
    target_filename: str
        The name of the file that proc needs
    suite_name: str
        Suite name (eg u-ab204)
    stream: str
        The model output stream to be processed
    input_dir: str
        The base directory of the current file directory
            (this excludes the suite name and the stream name)
    work_dir: str
        The base firectory for copying or symlinking

    Returns
    -------
    (full_path_file, full_path_dir, new_input_location): tuple
        tuple containing full path to file, full path to rootdir
        and new file location for copy/symlink
    """
    new_input_location = os.path.join(work_dir, suite_name, stream)

    # find files with arbitrary paths
    full_path_file = None
    full_path_dir = None
    suite_dir = os.path.join(input_dir, suite_name)
    for root, subdirs, ext in os.walk(suite_dir, followlinks=True):
        for subdir in subdirs:
            root_subdir = os.path.join(suite_dir, subdir)
            for _, _, filenames in os.walk(root_subdir, followlinks=True):
                for filename in filenames:
                    if filename == target_filename:
                        full_path_dir = root_subdir
                        full_path_file = os.path.join(root_subdir,
                                                      filename)
                        break

    return (full_path_file, full_path_dir, new_input_location)


def copy_to_staging_dir(expected_file,
                        old_input_location,
                        new_input_location,
                        ):
    """
    Copy data from old_input_location to new_input_location. These values
    should be constructed using the get_paths function in this module.
    Parameters
    ----------
    expected_files : list
        List of expected files conversion.
    old_input_location : str
        Location of input files.
    new_input_location : str
        Location to copy input files to.

    Returns
    -------
    : int
        Number of files copied.
    """

    logger = logging.getLogger(__name__)
    setup_logger(logger)

    # make new directory
    logger.info('Setting up staging directory:\n {dir}\n'
                ''.format(dir=new_input_location))
    if not os.path.exists(new_input_location):
        logger.info('Creating "{}"'.format(new_input_location))
        os.makedirs(new_input_location)

    # perform copies
    full_path_src = expected_file
    full_path_dest = new_input_location
    logger.info('copying file from {src} to {dest}'
                ''.format(src=full_path_src,
                          dest=full_path_dest))
    try:
        shutil.copy(full_path_src, full_path_dest)
    except IOError:
        logger.warn('Unable to copy file: {0}'.format(full_path_src))


def link_data(expected_file,
              old_input_location,
              new_input_location,
              ):
    """
    Identify data to be used and set up soft links only to the files
    that need to be read for this particular job step.

    Parameters
    ----------
    suite_name : str
        Suite name, e.g. `u-ar050`.
    stream : str
        Stream name, e.g. `ap5`, `inm`.
    start_date : datetime
        Start of this job step.
    end_date : datetime
        End of this job step.
    task_work_dir : str
        Working location for this cylc task, i.e. where to put the
        symlinks.
    input_dir : str
        Location to look for data.

    Returns
    -------
    : int
        Number of source files found.
    : str
        Location where symlinks have been created.
    """
    logger = logging.getLogger(__name__)
    setup_logger(logger)


    # Set up the symlink directory
    _setup_symlink_directory(new_input_location)
    # Identify files to link to and create links
    _create_symlinks(expected_file,
                     old_input_location,
                     new_input_location,
                     )
    return new_input_location


def _expected_ap(runid, stream, start_date, end_date):
    """
    Return a generator of the files expected from a UM output stream
    within the start and end dates

    Parameters
    ----------
    runid : str
        Suite RUNID as used in the output file names, i.e. for suite
        `u-ar050` the RUNID would be `ar050`.
    stream : str
        Stream name, e.g. `ap4`.
    start_date : datetime
        Start date for this step.
    end_date : datetime
        End date for this step.
    Returns
    -------
    : generator
        Generator returning start date, end date and file name for each
        expected file in the range supplied.
    """
    return _expected_common(_special_ap, runid, stream, start_date, end_date)


def _special_ap(date_num, runid, stream, file_date_step):
    file_start_date = TIME_UNIT.num2date(date_num)
    file_end_date = TIME_UNIT.num2date(date_num + file_date_step)
    if STREAM_FILES_PER_MONTH[stream] == 1:
        sub_yr = calendar.month_abbr[file_start_date.month].lower()
    else:
        sub_yr = '{:02d}{:02d}'.format(file_start_date.month,
                                       file_start_date.day)
    filename = '{}a.p{}{}{}.pp'.format(
        runid, stream[-1], file_start_date.year, sub_yr)
    return file_start_date, file_end_date, filename


def _expected_in(runid, stream, start_date, end_date):
    """
    Return a generator of the files expected from a CICE output stream
    within the start and end dates

    Parameters
    ----------
    runid : str
        Suite RUNID as used in the output file names, i.e. for suite
        `u-ar050` the RUNID would be `ar050`.
    stream : str
        Stream name, e.g. `inm`.
    start_date : datetime
        Start date for this step.
    end_date : datetime
        End date for this step.
    Returns
    -------
    : generator
        Generator returning start date, end date and file name for each
        expected file in the range supplied.
    """
    return _expected_common(_special_in, runid, stream, start_date, end_date)


def _special_in(date_num, runid, stream, file_date_step):
    file_start_date = TIME_UNIT.num2date(date_num)
    file_end_date = TIME_UNIT.num2date(date_num + file_date_step)
    filename = 'cice_{}i_1{}_{}-{}.nc'.format(
        runid, stream[-1], file_start_date.strftime('%Y%m%d'),
        file_end_date.strftime('%Y%m%d'))
    return file_start_date, file_end_date, filename


def _expected_on(runid, stream, start_date, end_date):
    """
    Return a generator of the files expected from a NEMO output stream
    within the start and end dates

    Parameters
    ----------
    runid : str
        Suite RUNID as used in the output file names, i.e. for suite
        `u-ar050` the RUNID would be `ar050`.
    stream : str
        Stream name, e.g. `onm`.
    start_date : datetime
        Start date for this step.
    end_date : datetime
        End date for this step.
    Returns
    -------
    : generator
        Generator returning tuple of start date, end date and file name
        for each expected file in the range supplied.
    """
    gen = itertools.chain(*[
        _expected_common(_special_on, runid, stream, start_date, end_date,
                         substream=substream)
        for substream in NEMO_SUBSTREAMS])
    return gen


def _special_on(date_num, runid, stream, file_date_step, substream=None):
    file_start_date = TIME_UNIT.num2date(date_num)
    file_end_date = TIME_UNIT.num2date(date_num + file_date_step)
    filename = 'nemo_{}o_1{}_{}-{}_{}.nc'.format(
        runid, stream[-1], file_start_date.strftime('%Y%m%d'),
        file_end_date.strftime('%Y%m%d'), substream)
    return file_start_date, file_end_date, filename


def _expected_common(file_name_formatter, runid, stream, start_date, end_date,
                     **kwargs):
    file_date_step = 30 // STREAM_FILES_PER_MONTH[stream]
    start_date_num = int(TIME_UNIT.date2num(start_date))
    end_date_num = int(TIME_UNIT.date2num(end_date))
    for date_num in range(start_date_num - file_date_step,
                          end_date_num + file_date_step, file_date_step):
        yield file_name_formatter(date_num, runid, stream,
                                  file_date_step, **kwargs)


def _setup_symlink_directory(new_input_location):
    """
    Create or empty the directory for the symlinks to be created and
    return its location.

    Parameters
    ----------
    new_input_location : path to directory to create symlinks in

    Returns
    -------
    : str
        Name of the directory that has been created.
    """
    logger = logging.getLogger(__name__)
    logger.info('Setting up symlink directory "{}"'.format(new_input_location))
    if not os.path.exists(new_input_location):
        logger.info('Creating "{}"'.format(new_input_location))
        os.makedirs(new_input_location)


def _create_symlinks(expected_file,
                     old_input_location,
                     new_input_location,
                     ):
    """
    Create the symlinks required for MIP Convert to run this task.

    Parameters
    ----------
    expected_file : str
        Single file expected for this task.
    old_input_location : str
        The location of the input filest the symlinks point to.
    new_input_location : str
        The location to use for the symlinks.

    Returns
    -------
    None
    """
    logger = logging.getLogger(__name__)
    logger.info('Looking for files in "{}"'.format(old_input_location))
    full_path_filename = expected_file
    full_path_link = os.path.join(new_input_location,
                                  os.path.basename(expected_file))
    # If there is a pre-existing link in the new_input_location then
    # remove it.
    if os.path.exists(full_path_link):
        logger.info('Removing existing symlink "{}"'
                    ''.format(full_path_link))
        os.remove(full_path_link)
        # create link if the file exists
    if os.path.exists(full_path_filename):
        msg1 = 'linking from {file} to {link}'\
            ''.format(file=full_path_filename,
                      link=full_path_link)
        logger.info(msg1)

        os.symlink(full_path_filename, full_path_link)
    else:
        logger.warning('Could not create symlink for "{}": '
                       'file not found.'.format(expected_file))
