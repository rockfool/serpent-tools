"""
System-wide methods for producing status update and errors.

See Also
--------
* https://docs.python.org/2/library/logging.html
* https://www.python.org/dev/peps/pep-0391/
"""

import functools
import warnings
import logging
from logging.config import dictConfig


class SerpentToolsException(Exception):
    """Base-class for all exceptions in this project"""
    pass


LOG_OPTS = ['critical', 'error', 'warning', 'info', 'debug']

loggingConfig = {
    'version': 1,
    'formatters': {
        'brief': {'format': '%(levelname)-8s: %(name)-12s: %(message)s'},
        'precise': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
            'level': logging.DEBUG,
            'stream': 'ext://sys.stdout'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': logging.INFO
    }
}

dictConfig(loggingConfig)

__logger__ = logging.getLogger('serpentTools')


def debug(message):
    """Log a debug message."""
    __logger__.debug('%s', message)


def info(message):
    """Log an info message, e.g. status update."""
    __logger__.info('%s', message)


def warning(message):
    """Log a warning that something that could go wrong or be avoided."""
    __logger__.warning('%s', message)


def error(message, fatal=True):
    """Log that something went wrong."""
    if fatal:
        __logger__.critical('%s', message, exc_info=True)
        raise SerpentToolsException('%s', message)
    __logger__.error('%s', message)


def updateLevel(level):
    """Set the level of the logger."""
    if level.lower() not in LOG_OPTS:
        __logger__.setLevel('INFO')
        warning('Logger option {} not in options. Set to info.'.format(level))
        return 'info'
    else:
        __logger__.setLevel(level.upper())
        return level


def depreciated(f):
    """Display a warning indicating a function will be depreciated."""

    @functools.wraps(f)
    def decoratedFunc(*args, **kwargs):
        msg = 'Call to depreciated function {}'.format(f.__name__)
        warning(msg)
        _updateFilterAlert(msg, DeprecationWarning)
        return f(*args, **kwargs)

    return decoratedFunc


def willChange(changeMsg):
    """Inform the user that some functionality may change."""

    def decorate(f):
        @functools.wraps(f)
        def decoratedFunc(*args, **kwargs):
            warning(changeMsg)
            _updateFilterAlert(changeMsg, FutureWarning)
            return f(*args, **kwargs)

        return decoratedFunc

    return decorate


def _updateFilterAlert(msg, category):
    warnings.simplefilter('always', category)
    warnings.warn(msg, category=category, stacklevel=3)
    warnings.simplefilter('default', category)