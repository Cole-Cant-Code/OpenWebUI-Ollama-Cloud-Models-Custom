"""
title: Sovereign Clock
author: Cole
author_url: https://github.com/Cole-Cant-Code
description: Current date, time, timezone, and temporal context. No dependencies.
required_open_webui_version: 0.4.0
version: 1.0.0
licence: MIT
"""

import time
from datetime import datetime, timezone


class Tools:
    def __init__(self):
        pass

    async def current_datetime(self) -> str:
        """
        Get the current date, time, timezone, and calendar context. Call this whenever you need to know what time it is, reference today's date, calculate relative dates, or make any time-sensitive statement.
        :return: Current datetime with full temporal context.
        """
        now = datetime.now()
        utc_now = datetime.now(timezone.utc)
        tz_name = time.tzname[time.daylight] if time.daylight else time.tzname[0]
        utc_offset = now.astimezone().strftime("%z")
        iso_week = now.isocalendar()

        return (
            f"- **Date:** {now.strftime('%A, %B %d, %Y')}\n"
            f"- **Time:** {now.strftime('%I:%M:%S %p')} {tz_name} (UTC{utc_offset[:3]}:{utc_offset[3:]})\n"
            f"- **UTC:** {utc_now.strftime('%Y-%m-%d %H:%M:%S')}Z\n"
            f"- **ISO Week:** {iso_week[0]}-W{iso_week[1]:02d}-{iso_week[2]}\n"
            f"- **Day:** {now.timetuple().tm_yday}/{'366' if now.year % 4 == 0 and (now.year % 100 != 0 or now.year % 400 == 0) else '365'}\n"
            f"- **Unix:** {int(time.time())}"
        )
