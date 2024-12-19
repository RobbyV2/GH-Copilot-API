import logging
from colorama import Fore, Style, init

init()


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        original_levelname = record.levelname

        colors = {
            "INFO": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.RED,
            "CRITICAL": Fore.RED + Style.BRIGHT,
            "DEBUG": Fore.BLUE,
        }

        if record.levelname in colors:
            record.levelname = (
                f"{colors[record.levelname]}{record.levelname}{Style.RESET_ALL}"
            )

        message = super().format(record)

        record.levelname = original_levelname

        return message


logger = logging.getLogger("gh_copilot_api")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = ColoredFormatter("%(levelname)s:\t  %(message)s")
console_handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(console_handler)
logger.propagate = False
