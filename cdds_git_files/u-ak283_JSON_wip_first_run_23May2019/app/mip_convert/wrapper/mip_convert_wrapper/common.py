# (C) British Crown Copyright 2017-2018, Met Office.
"""
Common routines for running mip_convert_wrapper
"""
import logging
import os
import sys


def print_env():
    """
    Return a string description of the environment variables (useful
    for debugging).

    Returns
    -------
    str
       Description of the current environment variables.
    """
    output = 'environment:\n'
    for env_var in sorted(os.environ.keys()):
        output += '    "{}" : "{}"\n'.format(env_var, os.environ[env_var])
    return output


def setup_logger(logger):
    """
    Set up the logger for printing to stdout.

    Parameters
    ----------
    logger : logging.Logger
        Logger to be set up
    """
    logger.setLevel(logging.DEBUG)
    logging.captureWarnings(True)
    logger.handlers = []
    streamhandler = logging.StreamHandler(sys.stdout)
    streamhandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(funcName)s '
                                  '%(levelname)s: %(message)s',
                                  datefmt='%Y-%m-%dT%H:%M:%S')
    streamhandler.setFormatter(formatter)
    logger.addHandler(streamhandler)
