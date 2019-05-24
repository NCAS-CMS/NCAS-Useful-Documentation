# (C) British Crown Copyright 2018, Met Office.
"""
Tests of mip_convert_wrapper.file_management
"""
import calendar
import datetime
import unittest
import mock
import os

from mip_convert_wrapper import TIME_UNIT, NEMO_SUBSTREAMS
from mip_convert_wrapper.file_management import (
    _expected_ap, _expected_in, _expected_on,
    get_paths, copy_to_staging_dir, link_data,
    )


class TestMisc(unittest.TestCase):
    """
    Test miscellaneous helper functions in the file_management.py module.
    """

    def test_get_paths(self):
        """
        Tests the file_management.get_paths function.
        """
        suite_name = 'u-RUNID'
        stream = 'ap4'
        start_date = TIME_UNIT.num2date(0)
        length1 = 360 * 5
        end_date = TIME_UNIT.num2date(length1)
        step = 30
        input_dir = os.path.sep + os.path.join('path', 'to', 'input', 'dir')
        work_dir = os.path.sep + os.path.join('path', 'to', 'work', 'dir')

        (expected_files_test,
         old_input_location_test,
         new_input_location_test,) = get_paths(suite_name,
                                               stream,
                                               start_date,
                                               end_date,
                                               input_dir,
                                               work_dir)

        expected_files_exp = generate_expected(_ap_formatter_1,
                                               step,
                                               stream,
                                               length1,
                                               )

        old_input_exp = os.path.join(input_dir,
                                     suite_name,
                                     stream,
                                     )
        new_input_exp = os.path.join(work_dir,
                                     suite_name,
                                     stream,
                                     )

        self.assertEqual(old_input_location_test,
                         old_input_exp,
                         'old_input_location not correct')

        self.assertEqual(new_input_location_test,
                         new_input_exp,
                         'new_input_location not correct')

        self.assertEqual([l1 for l1 in expected_files_test],
                         list(expected_files_exp))

    @mock.patch('os.path.exists')
    @mock.patch('shutil.copy')
    def test_copy_to_staging_dir(self,
                                 mock_shutil_copy2,
                                 mock_os_exists):
        """
        Tests the file_management.copy_to_staging_dir function.
        """
        src_dir = '/path/to/src/dir/'
        dest_dir = '/path/to/dest/dir/'
        start_dt = datetime.datetime(year=1850, month=1, day=1)
        end_dt = datetime.datetime(year=1854, month=12, day=30)
        expected_files = [(start_dt, end_dt, 'file1.nc'),
                          (start_dt, end_dt, 'file2.nc'),
                          (start_dt, end_dt, 'file3.nc')]

        mock_os_exists.return_value = True

        copy_to_staging_dir(expected_files, src_dir, dest_dir)

        copy2_calls_list = [mock.call(os.path.join(src_dir, f1),
                                     os.path.join(dest_dir, f1))
                           for sdt, edt, f1 in expected_files]

        mock_shutil_copy2.assert_has_calls(copy2_calls_list)

    @mock.patch('glob.glob')
    @mock.patch('os.symlink')
    @mock.patch('os.path.exists')
    def test_link_data(self,
                       mock_os_exists,
                       mock_os_symlink,
                       mock_glob_glob):
        """
        Tests the file_management.link_data function.
        """
        src_dir = '/path/to/src/dir/'
        dest_dir = '/path/to/dest/dir/'
        start_dt = datetime.datetime(year=1850, month=1, day=1)
        end_dt = datetime.datetime(year=1854, month=12, day=30)
        expected_files = [(start_dt, end_dt, 'file1.nc'),
                          (start_dt, end_dt, 'file2.nc'),
                          (start_dt, end_dt, 'file3.nc')]

        mock_glob_glob.return_value = []

        exists_returns = [True  ,]
        for _ in expected_files:
            exists_returns += [False, True,]
        mock_os_exists.side_effect = exists_returns

        num_links, link_dir = link_data(expected_files, src_dir, dest_dir)

        self.assertEqual(3, num_links)
        symlink_calls = [mock.call(os.path.join(src_dir, f1),
                                   os.path.join(dest_dir, f1))
                         for sdt, edt, f1 in expected_files]

        mock_os_symlink.assert_has_calls(symlink_calls)


class TestExpectedAP(unittest.TestCase):
    """
    Test expected file names for UM output streams.
    """
    def test_monthly(self):
        runid = 'RUNID'
        stream = 'ap4'
        start_date = TIME_UNIT.num2date(0)
        end_date = TIME_UNIT.num2date(360)
        step = 30
        expected = generate_expected(_ap_formatter_1, step, stream)
        actual = list(_expected_ap(runid, stream, start_date, end_date))
        self.assertEqual(expected, actual)

    def test_10day(self):
        runid = 'RUNID'
        stream = 'ap6'
        start_date = TIME_UNIT.num2date(0)
        end_date = TIME_UNIT.num2date(360)
        step = 10
        expected = generate_expected(_ap_formatter_3, step, stream)
        actual = list(_expected_ap(runid, stream, start_date, end_date))
        self.assertEqual(expected, actual)


class TestExpectedIN(unittest.TestCase):
    """
    Test expected file names for CICE output streams.
    """
    def test_monthly(self):
        runid = 'RUNID'
        stream = 'inm'
        start_date = TIME_UNIT.num2date(0)
        end_date = TIME_UNIT.num2date(360)
        step = 30
        expected = generate_expected(_in_formatter, step, stream)
        actual = list(_expected_in(runid, stream, start_date, end_date))
        self.assertEqual(expected, actual)

    def test_1day(self):
        runid = 'RUNID'
        stream = 'ind'
        start_date = TIME_UNIT.num2date(0)
        end_date = TIME_UNIT.num2date(360)
        step = 30
        expected = generate_expected(_in_formatter, step, stream)

        actual = list(_expected_in(runid, stream, start_date, end_date))
        self.assertEqual(expected, actual)


class TestExpectedON(unittest.TestCase):
    """
    Test expected files for NEMO output streams.
    """
    def test_monthly(self):
        runid = 'RUNID'
        stream = 'onm'
        start_date = TIME_UNIT.num2date(0)
        end_date = TIME_UNIT.num2date(360)
        step = 30
        expected = generate_expected_ocean(step, stream)
        actual = list(_expected_on(runid, stream, start_date, end_date))
        self.assertEqual(expected, actual)

    def test_1day(self):
        runid = 'RUNID'
        stream = 'ond'
        start_date = TIME_UNIT.num2date(0)
        end_date = TIME_UNIT.num2date(360)
        step = 30
        expected = generate_expected_ocean(step, stream)
        actual = list(_expected_on(runid, stream, start_date, end_date))
        self.assertEqual(expected, actual)


def generate_expected(file_name_formatter, step, stream, length=360):
    """
    Return a list of tuples representing the time bounds and name
    of each file expected.

    Parameters
    ----------
    file_name_formatter : function
        Function that takes the stream name (str) and the file start
        and end dates (datetimes) and returns a the file name expected
        as a string.
    step :  int
        Number of days between files, e.g. 10
    stream : str
        Name of the stream, e.g. 'ap4'

    Returns
    -------
    : list
        start time, end time and file name for each expected file.
    """
    expected = []
    for datenum in range(-step, length + step, step):
        file_start = TIME_UNIT.num2date(datenum)
        file_end = TIME_UNIT.num2date(datenum + step)
        file_name = file_name_formatter(stream, file_start, file_end)
        expected.append((file_start, file_end, file_name))
    return expected


def _ap_formatter_1(stream, file_start, file_end):
    month = calendar.month_abbr[file_start.month].lower()
    file_name = 'RUNIDa.p{}{}{}.pp'.format(
        stream[-1], file_start.year, month)
    return file_name


def _ap_formatter_3(stream, file_start, file_end):
    file_name = 'RUNIDa.p{}{}{:02d}{:02d}.pp'.format(
        stream[-1], file_start.year, file_start.month, file_start.day)
    return file_name


def _in_formatter(stream, file_start, file_end):
    file_name = 'cice_RUNIDi_1{}_{}-{}.nc'.format(
        stream[-1], file_start.strftime('%Y%m%d'),
        file_end.strftime('%Y%m%d'))
    return file_name


def generate_expected_ocean(step, stream):
    """
    Return a list of tuples representing the time bounds and name
    of each file expected in ocean streams.

    Parameters
    ----------
    step :  int
        Number of days between files, e.g. 10
    stream : str
        Name of the stream, e.g. 'ap4'

    Returns
    -------
    : list
        start time, end time and file name for each expected file.
    """
    expected = []
    for substream in NEMO_SUBSTREAMS:
        for datenum in range(-step, 360 + step, step):
            file_start = TIME_UNIT.num2date(datenum)
            file_end = TIME_UNIT.num2date(datenum + step)
            file_name = 'nemo_RUNIDo_1{}_{}-{}_{}.nc'.format(
                stream[-1], file_start.strftime('%Y%m%d'),
                file_end.strftime('%Y%m%d'), substream
            )
            expected.append((file_start, file_end, file_name))
    return expected


def _on_formatter(stream, file_start, file_end, substream=None):
    file_name = 'nemo_RUNIDi_1{}_{}-{}_{}.nc'.format(
        stream[-1], file_start.strftime('%Y%m%d'),
        file_end.strftime('%Y%m%d'),
        substream)
    return file_name


if __name__ == '__main__':
    unittest.main()
