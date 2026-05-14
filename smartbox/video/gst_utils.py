import logging

import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst

logger = logging.getLogger(__name__)


def init_gst() -> None:
    Gst.init(None)


def pick_decoder() -> str:
    return "vaapih264dec" if Gst.ElementFactory.find("vaapih264dec") else "avdec_h264"


def get_error_message(message) -> str:
    err, debug = message.parse_error()
    return f"{err.message}; {debug or ''}".strip()
