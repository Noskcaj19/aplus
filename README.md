# aplus

This tool lets you view your A+ attendance and submit codes if you can access A+ attendance through Canvas.

## Usage

    Usage: aplus.py [OPTIONS] CODE

    Options:
      -t, --token TEXT      Canvas LMS API token generated in settings  [required]
      -u, --base-url TEXT   Base url to your Canvas instance  [required]
      -c, --course-id TEXT  Course id to any course with A+ attendance enable,
                            optional but faster if provided
      -s, --show            Show attendance data
      --help                Show this message and exit.

An API token can be created at `<canvas-base-url>/profile/settings` under "Approved Integrations:".
The token can also be passed through the `$CANVAS_TOKEN` environment variable.
See the [Cavnas help page](https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273) for more info.

The course id can be found by accessing a course page and looking at the url: `<canvas-base-url>/courses/<course-id>`
Note: The course id included in the command **does not** need to be the same as the course you are submitting the code for.  Any course id works, ideally a course with A+ codes.
