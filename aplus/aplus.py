import html
import re
from datetime import datetime
from typing import Optional

import canvasapi
import click
import colorama
import requests
from canvasapi.external_tool import ExternalTool


class APlus:
    session: requests.Session
    body: str

    def __init__(self, tool: ExternalTool) -> None:
        super().__init__()
        self.session = requests.Session()

        url = tool.get_sessionless_launch_url()
        resp = self.session.get(url)
        form_entries = re.findall(r' <input type="hidden" name="(.*?)" id=".*" value="(.*?)" />', resp.text)
        if form_entries is None:
            raise Exception("Unable to locate form keys")
        resp = self.session.post(tool.url, {k: v for (k, v) in form_entries})

        self.body = resp.text

    def print_attendance(self):
        attendance_day_matches = re.findall(
            r'<div class="dayPanel" id="dayPanel_(.*?)" style="display:none;">(?:<div>\(Nothing on this day\)</div>|'
            r'<ul class="stv_list">(.+?)</ul>)</div>',
            self.body,
        )

        for (date_match, attendance_day_match) in attendance_day_matches:
            attendance_matches = re.findall(
                r'<li (?:class="stv_disabled")?><i class="fa (.+?)" aria-hidden="true"></i>(?:<a href="(.+?)">'
                r'(.+?)</a>|(.+?))</li>',
                attendance_day_match,
            )

            date = datetime.strptime(date_match, "%d_%b_%y")
            print(f'{Colors.bright(date.strftime("%B %d %Y"))}'
                  f'{" (today)" if is_same_day(date, datetime.now()) else ""}')
            if len(attendance_matches) == 0:
                print("  (Nothing on this day)")
            for (icon, link, active_course, inactive_course) in attendance_matches:
                if icon == "fa-check":
                    state_icon = "✔"
                elif icon == "fa-times":
                    state_icon = "✖"
                else:
                    state_icon = "?"
                class_entry = reformat_attendance_time(html.unescape(active_course or inactive_course).strip())
                print(
                    f'  {Colors.bright(state_icon)}'
                    f' {Colors.active_course(class_entry) if active_course else class_entry}'
                )


class Colors:
    @staticmethod
    def bright(string: str):
        return colorama.Style.BRIGHT + string + colorama.Style.NORMAL

    @staticmethod
    def active_course(string: str):
        return colorama.Fore.CYAN + colorama.Style.BRIGHT + string + colorama.Fore.RESET + colorama.Style.NORMAL


def is_same_day(one: datetime, two: datetime) -> bool:
    return one.year == two.year and one.month == two.month and one.day == two.day


def reformat_attendance_time(string: str):
    time_end = string.index("m") + 1
    time = datetime.strptime(string[:time_end], "%I:%M %p")
    return time.strftime("%I:%M %p") + string[time_end:]


def get_aplus(canvas, course_id) -> Optional[APlus]:
    for tool in canvas.get_course(course_id).get_external_tools(include_parents=True):
        if "aPlus" not in tool.name:
            continue
        return APlus(tool)


def show_attendance(aplus: APlus):
    aplus.print_attendance()


def show_attendance_callback(ctx, _p, v):
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
              help="Canvas LMS REST API token generated in settings")
@click.option("-u", "--base-url", required=True, type=str,
              help="Base url to your Canvas instance")
@click.option("-c", "--course-id", required=True, type=str,
              help="Course id to any course with A+ attendance enable")
@click.argument("code")
def aplus(show, token, base_url, course_id, code):
    colorama.init()
    canvas = canvasapi.Canvas(base_url, token)

    aplus = get_aplus(canvas, course_id)

    if show:
        show_attendance(aplus)
        return

    print("TODO: Implement code submission")


if __name__ == "__main__":
    aplus()
