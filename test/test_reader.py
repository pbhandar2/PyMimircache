# coding=utf-8
"""
this module tests CCacheReader and PyCacheReader

Author: Jason Yang <peter.waynechina@gmail.com> 2016/08

"""

import os
import sys

sys.path.append(os.path.join(os.getcwd(), "../"))

import unittest
import libMimircache.PyUtils as PyUtils
from PyMimircache.cacheReader.csvReader import CsvReader
from PyMimircache.cacheReader.plainReader import PlainReader
from PyMimircache.cacheReader.vscsiReader import VscsiReader
from PyMimircache.cacheReader.binaryReader import BinaryReader

DAT_FOLDER = "../data/"
if not os.path.exists(DAT_FOLDER):
    if os.path.exists("data/"):
        DAT_FOLDER = "data/"
    elif os.path.exists("../PyMimircache/data/"):
        DAT_FOLDER = "../PyMimircache/data/"


class CReaderTest(unittest.TestCase):
    def test_c_reader_vscsi(self):
        reader = PyUtils.setup_reader(trace_path="{}/trace.vscsi".format(DAT_FOLDER), trace_type='v', obj_id_type="l")
        PyUtils.reset_reader(reader)
        reader = PyUtils.setup_reader(f"{DAT_FOLDER}/trace.csv", 'p', obj_id_type="l")
        PyUtils.reset_reader(reader)
        reader = PyUtils.setup_reader(f"{DAT_FOLDER}/trace.csv", 'p', obj_id_type="c")
        PyUtils.reset_reader(reader)
        reader = PyUtils.setup_reader(f"{DAT_FOLDER}/trace.csv", 'c', data_type='c',
                                      init_params={"header": True, "delimiter": ",", "obj_id": 5, "size": 4, "real_time": 2})
        PyUtils.reset_reader(reader)
        reader = PyUtils.setup_reader(f"{DAT_FOLDER}/trace.csv", 'c', data_type='l',
                                      init_params={"header": True, "delimiter": ",", "obj_id": 5, "size": 4, "real_time": 2})
        PyUtils.reset_reader(reader)
        reader = PyUtils.setup_reader(f"{DAT_FOLDER}/trace.vscsi", 'b', data_type='l',
                                      init_params={"obj_id": 6, "real_time": 7, "fmt": "<3I2H2Q", "size": 2})
        PyUtils.reset_reader(reader)


class PyReaderTest(unittest.TestCase):
    def test_reader_v(self):
        reader = VscsiReader("{}/trace.vscsi".format(DAT_FOLDER))
        self.assertEqual(reader.get_num_of_req(), 113872)
        reader.reset()
        lines = 0
        for _ in reader:
            lines += 1
        self.assertEqual(lines, 113872)
        reader.reset()

        # verify read content
        first_request = reader.read_one_req()
        self.assertEqual(int(first_request), 42932745)

        t, req = reader.read_time_req()
        self.assertAlmostEqual(t, 5633898611441.0)
        self.assertEqual(req, 42932746)

    def test_reader_binary(self):
        reader = BinaryReader("{}/trace.vscsi".format(DAT_FOLDER), data_type='l',
                              init_params={"label": 6, "real_time": 7, "fmt": "<3I2H2Q"})
        self.assertEqual(reader.get_num_of_req(), 113872)
        reader.reset()
        lines = 0
        for _ in reader:
            lines += 1
        self.assertEqual(lines, 113872)
        reader.reset()

        # verify read content
        first_request = reader.read_one_req()
        self.assertEqual(int(first_request), 42932745)

        t, req = reader.read_time_req()
        self.assertAlmostEqual(t, 5633898611441.0)
        self.assertEqual(req, 42932746)

        line = reader.read_complete_req()
        self.assertListEqual(line, [2147483880, 512, 1, 42, 256, 42932747, 5633898745540])

    def test_reader_csv(self):
        reader = CsvReader("{}/trace.csv".format(DAT_FOLDER),
                           init_params={"header": True, "real_time": 2, "op": 3, "size": 4, 'label': 5,
                                        'delimiter': ','})
        self.assertEqual(reader.get_num_of_req(), 113872)
        reader.reset()
        lines = 0
        for _ in reader:
            lines += 1
        self.assertEqual(lines, 113872)
        reader.reset()

        # verify read content
        first_request = reader.read_one_req()
        self.assertEqual(first_request, "42932745")

        t, req = reader.read_time_req()
        self.assertAlmostEqual(t, 5633898611441.0)
        self.assertEqual(req, "42932746")

        line = reader.read_complete_req()
        self.assertListEqual(line, ['1', '5633898745540', '2a', '512', '42932747'])

    def test_reader_csv_datatype_l(self):
        reader = CsvReader("{}/trace.csv".format(DAT_FOLDER), data_type="l",
                           init_params={"header": True, "real_time": 2, "op": 3, "size": 4, 'label': 5,
                                        'delimiter': ','})
        self.assertEqual(reader.get_num_of_req(), 113872)
        reader.reset()
        lines = 0
        for _ in reader:
            lines += 1
        self.assertEqual(lines, 113872)
        reader.reset()

        # verify read content
        first_request = reader.read_one_req()
        self.assertEqual(first_request, 42932745)

        t, req = reader.read_time_req()
        self.assertAlmostEqual(t, 5633898611441.0)
        self.assertEqual(req, 42932746)

        line = reader.read_complete_req()
        self.assertListEqual(line, ['1', '5633898745540', '2a', '512', '42932747'])

    def test_reader_plain(self):
        reader = PlainReader("{}/trace.txt".format(DAT_FOLDER))
        self.assertEqual(reader.get_num_of_req(), 113872)
        reader.reset()
        lines = 0
        for _ in reader:
            lines += 1
        self.assertEqual(lines, 113872)
        reader.reset()

        # verify read content
        first_request = reader.read_one_req()
        self.assertEqual(first_request, "42932745")

    def test_reader_potpourri(self):
        v_reader = VscsiReader("{}/trace.vscsi".format(DAT_FOLDER))
        c_reader = CsvReader("{}/trace.csv".format(DAT_FOLDER), data_type="l",
                             init_params={"header": True, "real_time": 2, "op": 3, "size": 4, 'label': 5,
                                          'delimiter': ','})

        for req1, req2 in zip(v_reader, c_reader):
            self.assertEqual(req1, req2)

    def test_context_manager(self):
        with VscsiReader("{}/trace.vscsi".format(DAT_FOLDER)) as reader:
            self.assertEqual(reader.get_num_of_req(), 113872)


if __name__ == "__main__":
    unittest.main()
