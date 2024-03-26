"""torc package"""

import logging
import warnings

__version__ = "0.3.5"

logging.getLogger(__name__).addHandler(logging.NullHandler())
warnings.filterwarnings("once", category=DeprecationWarning)
