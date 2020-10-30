from functools import wraps
import sys
import logging
import logging.handlers
import os
import time

FMT = "%(asctime)s - %(name)s - %(module)s - %(levelname)s - %(message)s"


def setuplog(name, path=None, log_level=20, fmt=FMT):
    """Set-up the logging on sys.stdout"""
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    syslog = logging.handlers.SysLogHandler(address='/dev/log')
    syslog.setLevel(log_level)
    syslog.setFormatter(logging.Formatter(fmt))

    logger.addHandler(syslog)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)
    console.setFormatter(logging.Formatter(fmt))
    logger.addHandler(console)

    if path is not None:
        add_filehandler(logger, path, log_level=log_level, fmt=fmt)
    return logger


def add_filehandler(logger, path, log_level=20, fmt=FMT):
    """Add file handler to logger."""
    if os.path.dirname(path) != "":
        if not os.path.isdir(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
    isfile = os.path.isfile(path)
    if isfile:
        os.remove(path)
    ch = logging.FileHandler(path)
    ch.setFormatter(logging.Formatter(fmt))
    ch.setLevel(log_level)
    logger.addHandler(ch)
    if isfile:
        logger.debug(f"Overwriting log messages in file {path}.")
    else:
        logger.debug(f"Writing log messages to new file {path}.")

# writing to home directory for now.
# TODO switch to /var/log (probably use Syslog)
def start_logger(verbose, quiet, name="odm360"):
    if verbose:
        verbose = 2
    else:
        verbose = 1
    if quiet:
        quiet = 1
    else:
        quiet = 0
    log_level = max(10, 30 - 10 * (verbose - quiet))
    logger = setuplog(name, f"{name}.log", log_level=log_level)
    logger.info("starting...")
    return logger

# writing to home directory for now.
# TODO switch to /var/log (probably use Syslog)
def stream_logger(fn="odm360.log", truncate=100):
    # open file for reading
    with open(fn) as f:
        while True:
            yield f.read()
            time.sleep(0.2)
