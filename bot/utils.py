from collections import defaultdict
from datetime import datetime
from typing import Dict

import pytz
from datetime import tzinfo


def utc_offset_to_common_timezone() -> Dict[str, str]:
    dt = datetime.now(pytz.utc)
    zone_names = defaultdict(list)
    for tz in pytz.common_timezones:
        zone_names[dt.astimezone(pytz.timezone(tz)).utcoffset()].append(tz)

    zone_names = dict(zone_names)
    for tz_offset, tzs in zone_names.items():
        if len(tzs) >= 3:
            # trim the list longer than 3
            zone_names[tz_offset] = tzs[:3]

    return zone_names


def tz_to_abbr(tz: pytz.BaseTzInfo):
    abbr = tz.localize(datetime.now(), is_dst=None)
    return abbr.tzname()


def tzname_to_abbr(tzname: str):
    common_name = pytz.timezone(tzname)
    abbr = common_name.localize(datetime.now(), is_dst=None)
    return abbr.tzname()
