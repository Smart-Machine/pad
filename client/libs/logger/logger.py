import logging


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[95m",  # Magenta
    }
    RESET = "\033[0m"  # Reset color

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def get_colorful_logger(name="colorful_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = ColorFormatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    if not logger.hasHandlers():
        logger.addHandler(console_handler)

    return logger
