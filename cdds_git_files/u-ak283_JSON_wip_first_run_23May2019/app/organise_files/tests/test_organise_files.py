# (C) British Crown Copyright 2017-2018, Met Office.
# Please see LICENSE.rst for license details.
"""
Tests for the file organisation tools module.
"""
import datetime
import unittest
import mock
from mock import call


import organise_files


class TestOrganiseFiles(unittest.TestCase):
    """
    Simple tests of organise_files routines
    """

    @mock.patch('glob.iglob')
    @mock.patch('os.listdir')
    @mock.patch('os.path.exists')
    def test_identify_files_to_move(self,
                                    mock_exists,
                                    mock_listdir,
                                    mock_iglob):
        """
        Test the organise_files.identify_files_to_move() function.
        """
        mock_exists.return_value = True

        # inputs to the function
        root_dir = 'dummy'
        start_date = '1850'
        end_date = '1859'

        # setup list of file date ranges for input and output from function.
        # the test is selecting the 1850 and 1855 cycle from a range
        # 1850-1869
        input_year_list = [1850, 1855, 1860, 1865]
        output_year_list = [1850, 1855]
        date_list = [datetime.datetime(year=y1,
                                       month=1,
                                       day=1) for y1 in input_year_list]

        date_str_list = ['{dt1.year}-{dt1.month:02d}-{dt1.day:02d}'
                         ''.format(dt1=dt1) for dt1 in date_list]

        # create a list of files based on the date ranges and the specified
        # components and variables. These are fed in to the mock objects
        # and the expected output
        component_list = {'component_A': {'mip_table': 'mipA'},
                          'component_B': {'mip_table': 'mipB'},
                          }
        var_list = ['tas', 'prw']

        listdir_output = [date_str_list] + \
                         [list(component_list.keys()) for _ in date_list]
        mock_listdir.side_effect = listdir_output

        glob_list = []
        fname_template = '{v1}_{m1}_myExpriment_{d1.year}{d1.month}' \
                         + '-{d2.year}{d2.month}'

        cycle_dir_template = '{root}/{dt1.year}-{dt1.month:02d}-{dt1.day:02d}'
        comp_dir_template = cycle_dir_template + '/{comp}'

        expected_files = \
            dict([(component_list[comp1]['mip_table'],
                   dict([(v1, []) for v1 in var_list]))
                  for comp1 in component_list])
        expected_dirs = []
        for date1 in date_list:
            if date1.year in output_year_list:
                expected_dirs += [cycle_dir_template.format(root=root_dir,
                                                            dt1=date1)]
            for comp1 in component_list:
                file_list1 = []
                mip1 = component_list[comp1]['mip_table']
                for var1 in var_list:
                    ed1 = datetime.datetime(year=date1.year+4,
                                            month=12,
                                            day=31,
                                            )
                    fname1 = fname_template.format(v1=var1,
                                                   m1=mip1,
                                                   d1=date1,
                                                   d2=ed1,
                                                   )
                    file_list1 += [fname1]
                    if date1.year in output_year_list:
                        expected_files[mip1][var1] += [fname1]

                glob_list += [file_list1]
                if date1.year in output_year_list:
                    expected_dirs += [comp_dir_template.format(dt1=date1,
                                                               comp=comp1,
                                                               root=root_dir,
                                                               )]

        mock_iglob.side_effect = iter(glob_list)

        dirs, files = organise_files.identify_files_to_move(root_dir,
                                                            start_date,
                                                            end_date,
                                                            )

        self.assertEqual(sorted(dirs), sorted(expected_dirs))
        self.assertDictEqual(files, expected_files)

    @mock.patch('shutil.move')
    @mock.patch('os.path.isdir')
    @mock.patch('os.mkdir')
    def test_move_files(self, mock_mkdir, mock_isdir, mock_move):
        """
        Test the organise_files.move_files() function.
        """

        mock_isdir.return_value = False
        files_to_move = {'A': {'prw': ['prw_A_date1.nc', 'prw_A_date2.nc'],
                               'tas': ['tas_A_date1.nc', 'tas_A_date2.nc']},
                         'O': {'tos': ['tos_O_date1.nc', 'tos_O_date2.nc'],
                               'sos': ['sos_O_date1.nc', 'sos_O_date2.nc']}}
        organise_files.move_files(files_to_move, 'location')
        mock_mkdir.assert_has_calls([call('location/A'),
                                     call('location/A/prw'),
                                     call('location/A/tas'),
                                     call('location/O'),
                                     call('location/O/tos'),
                                     call('location/O/sos')])
        mock_move.assert_has_calls([call('prw_A_date1.nc', 'location/A/prw'),
                                    call('prw_A_date2.nc', 'location/A/prw'),
                                    call('tas_A_date1.nc', 'location/A/tas'),
                                    call('tas_A_date2.nc', 'location/A/tas'),
                                    call('tos_O_date1.nc', 'location/O/tos'),
                                    call('tos_O_date2.nc', 'location/O/tos'),
                                    call('sos_O_date1.nc', 'location/O/sos'),
                                    call('sos_O_date2.nc', 'location/O/sos')])


if __name__ == '__main__':
    unittest.main()
