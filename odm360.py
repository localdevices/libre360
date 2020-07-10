#!/usr/bin/python3
"""
Run odm360 with arguments

arguments:
-p or --parent: run as parent (if not set, run as child)
-d or --destination: provide a path name to
"""
from odm360.log import setuplog
import gphoto2 as gp
from optparse import OptionParser

def main():
    parser = create_parser()
    (options, args) = parser.parse_args()
    if options.parent:
        camera_list = list(gp.Camera.autodetect())
        if len(camera_list) > 0:
            # gphoto2 compatible cameras are found, assume a gphoto2 rig
            from odm360.workflows import parent_gphoto2 as workflow

        else:
            # no gphoto2 compatible cameras found, assume serial or ip connection rig
            if options.serial:
                from odm360.workflows import parent_serial as workflow
            else:
                from odm360.workflows import parent_server as workflow


    else:
        options.root = None # should come from server
        if options.serial:
            from odm360.workflows import child_serial as workflow
        else:
            from odm360.workflows import child_tcp_ip as workflow

        # you are a child, so act like one!

    # start a logger with defined log levels. This may be used in our main call
    if options.verbose:
        verbose = 2
    else:
        verbose = 1
    if options.quiet:
        quiet = 1
    else:
        quiet = 0
    log_level = max(10, 30 - 10 * (verbose - quiet))

    logger = setuplog("odm360", "odm360.log", log_level=log_level)
    logger.info("starting...")

    workflow(options.dt, root=options.root, logger=logger)

def create_parser():
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option('-q', '--quiet',
                      dest='quiet', default=False, action='store_false',
                      help='do not print status messages to stdout')
    parser.add_option('-v', '--verbose',
                      dest='verbose', default=False, action='store_false',
                      help='print extra debug status messages to stdout')
    parser.add_option('-p', '--parent',
                      dest='parent', default=False, action='store_true',
                      help='Start odm360 as parent (default: run as child)')
    parser.add_option('-s', '--serial',
                      dest='serial', default=False, action='store_true',
                      help='Start odm360 parent as serial connection (default: run with socket TCP connection, only used with parent)')
    parser.add_option('-d', '--destination',
                      dest='root', default='.', nargs=1,
                      help='Local path for storing photos')
    parser.add_option('-t', '--time',
                      dest='dt', default=5, nargs=1,
                      help='Number of seconds between each photo')
    return parser

if __name__ == "__main__":
    main()

