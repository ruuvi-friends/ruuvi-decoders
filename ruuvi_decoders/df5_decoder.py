from __future__ import division

import math
import logging
import struct

log = logging.getLogger(__name__)


class Df5Decoder(object):
    """
    Decodes data from RuuviTag with Data Format 5
    Protocol specification:
    https://github.com/ruuvi/ruuvi-sensor-protocols
    """

    def _get_temperature(self, data):
        """Return temperature in celsius"""
        if data[1] == -32768:
            return None

        return round(data[1] / 200, 2)

    def _get_humidity(self, data):
        """Return humidity %"""
        if data[2] == 65535:
            return None

        return round(data[2] / 400, 2)

    def _get_pressure(self, data):
        """Return air pressure hPa"""
        if data[3] == 0xFFFF:
            return None

        return round((data[3] + 50000) / 100, 2)

    def _get_acceleration(self, data):
        """Return acceleration mG"""
        if (data[4] == -32768 or data[5] == -32768 or data[6] == -32768):
            return (None, None, None)

        return data[4:7]

    def _get_powerinfo(self, data):
        """Return battery voltage and tx power"""
        battery_voltage = data[7] >> 5
        tx_power = data[7] & 0x001F

        return (battery_voltage, tx_power)

    def _get_battery(self, data):
        """Return battery mV"""
        battery_voltage = self._get_powerinfo(data)[0]
        if battery_voltage == 0b11111111111:
            return None

        return battery_voltage + 1600

    def _get_txpower(self, data):
        """Return transmit power"""
        tx_power = self._get_powerinfo(data)[1]
        if tx_power == 0b11111:
            return None

        return -40 + (tx_power * 2)

    def _get_movementcounter(self, data):
        return data[8]

    def _get_measurementsequencenumber(self, data):
        return data[9]

    def _get_mac(self, data):
        return ''.join('{:02x}'.format(x) for x in data[10:])

    def decode_data(self, data):
        """
        Decode sensor data.

        Returns:
            dict: Sensor values
        """
        try:
            byte_data = struct.unpack(
                '>BhHHhhhHBH6B', bytearray.fromhex(data[:48])
            )

            acc_x, acc_y, acc_z = self._get_acceleration(byte_data)
            return {
                'data_format': 5,
                'humidity': self._get_humidity(byte_data),
                'temperature': self._get_temperature(byte_data),
                'pressure': self._get_pressure(byte_data),
                'acceleration': math.sqrt(
                    acc_x * acc_x + acc_y * acc_y + acc_z * acc_z
                ),
                'acceleration_x': acc_x,
                'acceleration_y': acc_y,
                'acceleration_z': acc_z,
                'tx_power': self._get_txpower(byte_data),
                'battery': self._get_battery(byte_data),
                'movement_counter': self._get_movementcounter(byte_data),
                'measurement_sequence_number':
                    self._get_measurementsequencenumber(byte_data),
                'mac': self._get_mac(byte_data)
            }
        except Exception:
            log.exception('Value: %s not valid', data)
            return None
