""" tests / pmon / unit / test_protocol_pi30.py """
import unittest

from powermon.commands.command import Command  # , CommandType
# from powermon.commands.command_definition import CommandDefinition
# from powermon.commands.reading_definition import ReadingType, ResponseType
# from powermon.commands.result import ResultType
from powermon.device import DeviceInfo
from powermon.libs.errors import InvalidCRC, InvalidResponse
from powermon.outputformats.simple import SimpleFormat
from powermon.protocols.pi30 import PI30 as Proto

# import construct as cs

proto = Proto()


class TestProtocolPi30(unittest.TestCase):
    """ exercise different functions in PI30 protocol """

    def test_check_crc(self):
        """ test a for correct CRC validation """
        _result = proto.check_crc(response=b"(0 100 0 0 1 532 532 450 0000 0030\x0e\x5E\n", command_definition=proto.get_command_definition('QBMS'))
        # print(_result)
        self.assertTrue(_result)

    def test_check_crc_incorrect(self):
        """ test an exception is raised if CRC validation fails """
        self.assertRaises(InvalidCRC, proto.check_crc, response=b"(0 100 0 0 1 532 532 450 0000 0030\x0e\x5D\n", command_definition=proto.get_command_definition('QBMS'))

    def test_trim(self):
        """ test protocol does a correct trim operation """
        _result = proto.trim_response(response=b"(0 100 0 0 1 532 532 450 0000 0030\x0e\x5E\n", command_definition=proto.get_command_definition('QBMS'))
        expected = b'0 100 0 0 1 532 532 450 0000 0030'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_check_valid_ok(self):
        """ test protocol returns true for a correct response validation check """
        _result = proto.check_valid(response=b"(0 100 0 0 1 532 532 450 0000 0030\x0e\x5E\n")
        expected = True
        # print(_result)
        self.assertEqual(_result, expected)

    def test_check_valid_none(self):
        """ test protocol returns false for a None response validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=None)

    def test_check_valid_short(self):
        """ test protocol returns false for a short response validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=b"(0")

    def test_check_valid_missing(self):
        """ test protocol returns false for a response missing start char validation check """
        self.assertRaises(InvalidResponse, proto.check_valid, response=b"0 100 0 0 1 532 532 450 0000 0030\x0e\x5E\n")

    def test_full_command_qbms(self):
        """ test a for correct full command for QBMS """
        _result = proto.get_full_command(command="QBMS")
        expected = b'QBMSaD\r'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_build_result_qbms(self):
        """ test result build for QBMS """
        expected = [
            'battery_is_connected=True',
            'battery_capacity_from_bms=100%',
            'battery_charging_is_forced=False',
            'battery_discharge_is_enabled=True',
            'battery_charge_is_enabled=False',
            'battery_bulk_charging_voltage_from_bms=53.2V',
            'battery_float_charging_voltage_from_bms=53.2V',
            'battery_cut-off_voltage_from_bms=45.0V',
            'battery_max_charging_current=0A',
            'battery_max_discharge_current=30A']
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", device_id="device_id", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QBMS"})
        command.command_definition = proto.get_command_definition('QBMS')
        _result = command.build_result(raw_response=b"(0 100 0 0 1 532 532 450 0000 0030\x0e\x5E\n", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_full_command_qvfw(self):
        """ test a for correct full command for QVFW """
        _result = proto.get_full_command(command="QVFW")
        expected = b'QVFWb\x99\r'
        # print(_result)
        self.assertEqual(_result, expected)

    def test_build_result_qvfw(self):
        """ test result build for QVFW """
        expected = ['main_cpu_firmware_version=00072.70']
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", device_id="device_id", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QVFW"})
        command.command_definition = proto.get_command_definition('QVFW')
        _result = command.build_result(raw_response=b"(VERFW:00072.70\x53\xA7\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)

    def test_build_result_qvfw_incorrect_crc(self):
        """ test result build for QVFW with an incorrect CRC"""
        expected = ['Error Count: 1',
            "Error #0: response has invalid CRC - got '\\x53\\xa6', calculated '\\x53\\xa7'"]
        simple_formatter = SimpleFormat({"extra_info": True})
        device_info = DeviceInfo(name="name", device_id="device_id", model="model", manufacturer="manufacturer")
        command = Command.from_config({"command": "QVFW"})
        command.command_definition = proto.get_command_definition('QVFW')
        _result = command.build_result(raw_response=b"(VERFW:00072.70\x53\xA6\r", protocol=proto)
        formatted_data = simple_formatter.format(command, _result, device_info)
        # print(formatted_data)
        self.assertEqual(formatted_data, expected)
