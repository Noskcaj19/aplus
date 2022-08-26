import html
import re
from datetime import datetime, timezone

import requests
from canvasapi.external_tool import ExternalTool

from aplus.colors import Colors

LOCAL_TIMEZONE = datetime.now(timezone.utc).astimezone().tzinfo


class NoAvailableCodesException(Exception):
    pass


class APlus:
    session: requests.Session
    body: str
    base_url: str

    def __init__(self, tool: ExternalTool) -> None:
        super().__init__()
        self.session = requests.Session()

        url = tool.get_sessionless_launch_url()
        resp = self.session.get(url)
        form_entries = re.findall(
            r'<input type="hidden" name="(.*?)" id=".*?" value="(.*?)" />', resp.text
        )
        if form_entries is None:
            raise Exception("Unable to locate form keys")
        resp = self.session.post(
            tool.url, {k: html.unescape(v) for (k, v) in form_entries}
        )

        self.base_url = resp.url.split("?", 1)[0]
        self.body = resp.text

    def get_history(self):
        attendance_day_matches = re.findall(
            r'<div class="dayPanel" id="dayPanel_(.*?)" style="display:none;">(?:<div>\(Nothing on this day\)</div>|'
            r'<ul class="stv_list">(.+?)</ul>)</div>',
            self.body,
        )
        out = []
        for (date_match, attendance_day_match) in attendance_day_matches:

            attendance_matches = re.findall(
                r'<li (?:class="stv_disabled")?><i class="fa (.+?)" aria-hidden="true"></i>(?:<a href="(.+?)">'
                r"(.+?)</a>|(.+?))</li>",
                attendance_day_match,
            )
            current_date = []
            date = datetime.strptime(date_match, "%d_%b_%y")
            for (icon, link, active_course, inactive_course) in attendance_matches:
                if icon == "fa-check":
                    state = "submitted"
                elif icon == "fa-times":
                    state = "not-submitted"
                else:
                    state = "unknown"
                class_entry = self._reformat_attendance_time(
                    html.unescape(active_course or inactive_course).strip()
                )
                current_date.append(
                    (
                        date,
                        {
                            "link": link,
                            "class_entry": class_entry,
                            "active": bool(active_course),
                            "state": state,
                        },
                    )
                )
            out.append(current_date)
        return out

    def print_attendance(self):
        attendance_day_matches = re.findall(
            r'<div class="dayPanel" id="dayPanel_(.*?)" style="display:none;">(?:<div>\(Nothing on this day\)</div>|'
            r'<ul class="stv_list">(.+?)</ul>)</div>',
            self.body,
        )

        for (date_match, attendance_day_match) in attendance_day_matches:
            attendance_matches = re.findall(
                r'<li (?:class="stv_disabled")?><i class="fa (.+?)" aria-hidden="true"></i>(?:<a href="(.+?)">'
                r"(.+?)</a>|(.+?))</li>",
                attendance_day_match,
            )

            date = datetime.strptime(date_match, "%d_%b_%y")
            print(
                f'{Colors.bright(date.strftime("%B %d %Y"))}'
                f'{Colors.today(" (today)") if self._is_same_day(date, datetime.now()) else ""}'
            )
            if len(attendance_matches) == 0:
                print("  (Nothing on this day)")
            for (icon, link, active_course, inactive_course) in attendance_matches:
                if icon == "fa-check":
                    state_icon = Colors.check("✔")
                elif icon == "fa-times":
                    state_icon = Colors.error("✖")
                else:
                    state_icon = Colors.question("?")
                class_entry = self._reformat_attendance_time(
                    html.unescape(active_course or inactive_course).strip()
                )
                print(
                    f"  {state_icon}"
                    f" {Colors.active_course(class_entry) if active_course else class_entry}"
                )

    def submit_code(self, code: str):
        links = re.findall(
            r'<li ><i class="fa fa-.*?" aria-hidden="true"></i><a href="(.+?)">.+?</a></li>',
            self.body,
        )
        if len(links) == 0:
            raise NoAvailableCodesException()
        link = links[0]

        submission_page = self.session.get(self.base_url + link[1:])
        form_entries = re.findall(
            r'<input type="hidden" name="(.*?)" id=".*?" value="(.*?)" />',
            submission_page.text,
        )

        submit_data = re.findall(
            r'<input type="submit" name="(.*?)" value="(.*?)" id=".*?" class=".*?" />',
            submission_page.text,
        )[0]
        form_entries.append(submit_data)

        input_key_name = re.findall(
            r'<input name="(.*?)" type="text" id=".*?" placeholder=".*?" />',
            submission_page.text,
        )[0]
        form_entries.append((input_key_name, code))

        resp = self.session.post(
            self.base_url + link, {k: v for (k, v) in form_entries}
        )

        if not (resp.status_code == 302 or resp.status_code == 200):
            raise Exception(f"Unknown status code: {resp.status_code}")
        elif 'class="errorMessage"' in resp.text:
            print("error")
        else:
            print("success")

    @staticmethod
    def _is_same_day(one: datetime, two: datetime) -> bool:
        return one.year == two.year and one.month == two.month and one.day == two.day

    @staticmethod
    def _reformat_attendance_time(string: str):
        (year, month, day, hour, minute, second, text) = re.search(
            r'<script type="text/javascript">writeLocalTime\(Date\.UTC\((.+?),(.+?),(.+?),(.+?),(.+?),(.+?)\)\);</script>(.+?)$',
            string,
        ).groups()
        time_utc = datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second), tzinfo=timezone.utc)
        time_local = time_utc.astimezone(LOCAL_TIMEZONE)
        return time_local.strftime("%I:%M %p") + text
