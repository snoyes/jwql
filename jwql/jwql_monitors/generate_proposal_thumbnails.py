#! /usr/bin/env python

"""Generate thumbnails for each proposal to be used for display in
the archive page of the web app.

In the web app, each instrument has its own 'archive' page where users
may view JWST images for the particular instrument.  The page displays
buttons for each proposal with a thumbnail image from each particular
proposal.  This script goes through the thumbnail filesystem and
creates the thumbnail to display based on the first existing rate file.
The thumbnail is saved as ``<proposal_id>.thumb``.

Authors
-------

    - Matthew Bourque

Use
---

    This script is intended to be executed as such:

    ::

        python generate_proposal_thumbnails.py
"""

import glob
import logging
import os
import shutil

from jwql.utils.logging_functions import log_info, log_fail
from jwql.utils.utils import get_config
from jwql.utils.monitor_utils import initialize_instrument_monitor, update_monitor_table
from jwql.utils.protect_module import lock_module

SETTINGS = get_config()


@log_fail
@log_info
def generate_proposal_thumbnails():
    """The main function of the ``generate_proposal_thumbnails`` module.
    See module docstring for further details."""

    proposal_dirs = glob.glob(os.path.join(SETTINGS['thumbnail_filesystem'], '*'))

    for proposal_dir in proposal_dirs:
        rate_thumbnails = glob.glob(os.path.join(proposal_dir, '*rate*.thumb'))
        dark_thumbnails = glob.glob(os.path.join(proposal_dir, '*dark*.thumb'))
        uncal_thumbnails = glob.glob(os.path.join(proposal_dir, '*uncal*.thumb'))
        if rate_thumbnails:
            thumbnail = rate_thumbnails[0]
        elif dark_thumbnails:
            thumbnail = dark_thumbnails[0]
        elif uncal_thumbnails:
            thumbnail = uncal_thumbnails[0]
        else:
            thumbnail = None
            logging.info('No uncal, dark,  or rate files found for {}.  No thumbnail generated.'.format(proposal_dir))

        if thumbnail:
            proposal = os.path.basename(thumbnail)[0:7]
            outfile = os.path.join(proposal_dir, '{}.thumb'.format(proposal))
            shutil.copy2(thumbnail, outfile)
            logging.info('Copied {} to {}'.format(thumbnail, outfile))


@lock_module
def protected_code():
    """Protected code ensures only 1 instance of module will run at any given time"""
    module = os.path.basename(__file__).strip('.py')
    start_time, log_file = initialize_instrument_monitor(module)

    generate_proposal_thumbnails()
    update_monitor_table(module, start_time, log_file)


if __name__ == '__main__':
    protected_code()
