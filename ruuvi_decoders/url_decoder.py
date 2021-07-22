from __future__ import division

import base64
import logging

log = logging.getLogger(__name__)


class UrlDecoder(object):
    """
    Decodes data from RuuviTag url
    Protocol specification:
    https://github.com/ruuvi/ruuvi-sensor-protocols

    Decoder operations are ported from:
    https://github.com/ruuvi/sensor-protocol-for-eddystone-url/blob/master/index.html

    0:   uint8_t     format;          // (0x02 = realtime sensor readings)
    1:   uint8_t     humidity;        // one lsb is 0.5%
    2-3: uint16_t    temperature;     // Signed 8.8 fixed-point notation.
    4-5: uint16_t    pressure;        // (-50kPa)
    6-7: uint16_t    time;            // seconds (now from reset)

    The bytes for temperature, pressure and time are swaped during the encoding
    """

    def _get_temperature(self, decoded):
        """Return temperature in celsius"""
        temp = (decoded[2] & 127) + decoded[3] / 100
        sign = (decoded[2] >> 7) & 1
        if sign == 0:
            return round(temp, 2)
        return round(-1 * temp, 2)

    def _get_humidity(self, decoded):
        """Return humidity %"""
        return decoded[1] * 0.5

    def _get_pressure(self, decoded):
        """Return air pressure hPa"""
        pres = ((decoded[4] << 8) + decoded[5]) + 50000
        return pres / 100

    def decode_data(self, encoded):
        """
        Decode sensor data.

        Returns:
            dict: Sensor values
        """
        try:
            identifier = None
            data_format = 2
            if len(encoded) > 8:
                data_format = 4
                identifier = encoded[8:]
                encoded = encoded[:8]
            decoded = bytearray(base64.b64decode(encoded, '-_'))
            return {
                'data_format': data_format,
                'temperature': self._get_temperature(decoded),
                'humidity': self._get_humidity(decoded),
                'pressure': self._get_pressure(decoded),
                'identifier': identifier
            }
        except:
            log.exception('Encoded value: %s not valid', encoded)
            return None
