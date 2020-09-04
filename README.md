# aplus

This tool lets you view your A+ attendance and submit codes if you can access A+ attendance through Canvas.

## Usage

    Usage: aplus.py [OPTIONS] CODE

    Options:
      -s, --show            Show attendance data
      -t, --token TEXT      Canvas LMS API token generated in settings  [required]
      -u, --base-url TEXT   Base url to your Canvas instance  [required]
      -c, --course-id TEXT  Course id to any course with A+ attendance enable
                            [required]

      --help                Show this message and exit.

An API token can be created at `<canvas-base-url>/profile/settings` under "Approved Integrations:".
The token can also be passed through the `$CANVAS_TOKEN` environment variable.

The course id can be found by accessing a course page and looking at the url: `<canvas-base-url>/courses/<course-id>`