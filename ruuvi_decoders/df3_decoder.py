from __future__ import division

import base64
import math
import logging
import struct

log = logging.getLogger(__name__)


class Df3Decoder(object):
    """
    Decodes data from RuuviTag with Data Format 3
    Protocol specification:
    https://github.com/ruuvi/ruuvi-sensor-protocols
    """

    def _get_temperature(self, data):
        """Return temperature in celsius"""

        # The temperature is in two fields, one for the integer part,
        # one for the fraction
        #
        # The integer part was decoded as a signed two's complement number,
        # but this isn't how it's really stored. The MSB is a sign, the lower
        # 7 bits are the unsigned temperature value.
        #
        # To convert from the decoded value we have to add 128 and then negate,
        # if the decoded value was negative
        frac = data[3] / 100
        if data[2] < 0:
            return -(data[2] + 128 + frac)
        else:
            return data[2] + frac

    def _get_humidity(self, data):
        """Return humidity %"""
        return data[1] * 0.5

    def _get_pressure(self, data):
        """Return air pressure hPa"""
        return (data[4] + 50000) / 100

    def _get_acceleration(self, data):
        """Return acceleration mG"""
        return data[5:8]

    def _get_battery(self, data):
        """Return battery mV"""
        return data[8]

    def decode_data(self, data):
        """
        Decode sensor data.

        Returns:
            dict: Sensor values
        """
        try:
            byte_data = struct.unpack('>BBbBHhhhH', bytearray.fromhex(data[:28]))
            acc_x, acc_y, acc_z = self._get_acceleration(byte_data)
            return {
                'data_format': 3,
                'humidity': self._get_humidity(byte_data),
                'temperature': self._get_temperature(byte_data),
                'pressure': self._get_pressure(byte_data),
                'acceleration': math.sqrt(
                    acc_x * acc_x + acc_y * acc_y + acc_z * acc_z),
                'acceleration_x': acc_x,
                'acceleration_y': acc_y,
                'acceleration_z': acc_z,
                'battery': self._get_battery(byte_data)
            }
        except Exception:
            log.exception('Value: %s not valid', data)
            return None