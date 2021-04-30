"""Top-level package for Ruuvi Decoders."""

__author__ = """Sergio Isidoro"""
__email__ = 'smaisidoro@gmail.com'
__version__ = '0.1.0'
import logging
from ruuvi_decoders.url_decoder import UrlDecoder
from ruuvi_decoders.df3_decoder import Df3Decoder
from ruuvi_decoders.df5_decoder import Df5Decoder

log = logging.getLogger(__name__)

def get_decoder(data_type):
    """
    Get correct decoder for Data Type.

    Returns:
        object: Data decoder
    """
    if data_type == 2:
        log.warning("DATA TYPE 2 IS OBSOLETE. UPDATE YOUR TAG")
        # https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_04.md
        return UrlDecoder()
    if data_type == 4:
        log.warning("DATA TYPE 4 IS OBSOLETE. UPDATE YOUR TAG AND SWITCH MODE")
        # https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_04.md
        return UrlDecoder()
    if data_type == 3:
        log.warning("DATA TYPE 3 IS DEPRECATED - UPDATE YOUR TAG")
        # https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_03.md
        return Df3Decoder()
    return Df5Decoder()
