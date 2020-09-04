from typing import Optional

import canvasapi
import click
import colorama

from aplus.aplus import APlus, NoAvailableCodesException


def get_aplus(canvas, course_id: str) -> Optional[APlus]:
    for tool in canvas.get_course(course_id).get_external_tools(include_parents=True):
        if "aPlus" not in tool.name:
            continue
        return APlus(tool)


def show_attendance(aplus: APlus):
    aplus.print_attendance()


def show_attendance_callback(ctx: click.Context, _p: click.Option, v: bool):
    if not v:
        return v
    for opt in ctx.command.params:
        if opt.name != "code":
            continue
        opt.required = False
    return v


@click.command()
@click.option("-s", "--show", is_flag=True, callback=show_attendance_callback, is_eager=True,
              help="Show attendance data")
@click.option("-t", "--token", required=True, type=str, envvar="CANVAS_TOKEN",
              help="Canvas LMS API token generated in settings")
@click.option("-u", "--base-url", required=True, type=str,
              help="Base url to your Canvas instance")
@click.option("-c", "--course-id", required=True, type=str,
              help="Course id to any course with A+ attendance enable")
@click.argument("code")
def aplus(show: bool, token: str, base_url: str, course_id: str, code: str):
    colorama.init()
    canvas = canvasapi.Canvas(base_url, token)

    aplus = get_aplus(canvas, course_id)

    if show:
        show_attendance(aplus)
        return

    try:
        aplus.submit_code(code)
    except NoAvailableCodesException:
        print("No open codes")
        exit(2)


if __name__ == "__main__":
    aplus()
