import logging
import os
from pathlib import Path

import macleod.parsing.Parser

logging.config.fileConfig(str(Path.home().joinpath('.macleod').joinpath('logging.conf')))

# Setup our package level logger
LOGGER = logging.getLogger(__name__)
LOGGER.debug('Loaded configuration for sub-package Logger')

all = [LOGGER]
