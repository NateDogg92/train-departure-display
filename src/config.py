import os
import re

# validate platform number
def parsePlatformData(platform):
    if platform is None:
        return ""
    elif bool(re.match(r'^(?:\d{1,2}[A-D]|[A-D]|\d{1,2})$', platform)):
        return platform
    else:
        return ""

def parsePlatformSchedule(schedule_str):
    if not schedule_str:
        return []
    entries = []
    pattern = re.compile(r'^(\d{1,2}:\d{2})-(\d{1,2}:\d{2})=(.+)$')
    for entry in schedule_str.split(','):
        m = pattern.match(entry.strip())
        if m:
            platform = parsePlatformData(m.group(3).strip())
            if platform:
                entries.append({'start': m.group(1), 'end': m.group(2), 'platform': platform})
    return entries

def loadConfig():
    data = {
        "journey": {},
        "api": {}
    }

    data["targetFPS"] = int(os.getenv("targetFPS") or 70)
    data["refreshTime"] = int(os.getenv("refreshTime") or 180)
    data["fpsTime"] = int(os.getenv("fpsTime") or 180)
    data["screenRotation"] = int(os.getenv("screenRotation") or 2)
    data["screenBlankHours"] = os.getenv("screenBlankHours") or ""
    data["headless"] = False
    if os.getenv("headless", "").upper() == "TRUE":
        data["headless"] = True

    data["debug"] = False
    if os.getenv("debug", "").upper() == "TRUE":
        data["debug"] = True
    else:
        if os.getenv("debug") and os.getenv("debug").isnumeric():
            data["debug"] = int(os.getenv("debug"))

    data["dualScreen"] = False
    if os.getenv("dualScreen", "").upper() == "TRUE":
        data["dualScreen"] = True
    data["firstDepartureBold"] = True
    if os.getenv("firstDepartureBold", "").upper() == "FALSE":
        data["firstDepartureBold"] = False
    data["hoursPattern"] = re.compile("^((2[0-3]|[0-1]?[0-9])-(2[0-3]|[0-1]?[0-9]))$")

    data["journey"]["departureStation"] = os.getenv("departureStation") or "PAD"

    data["journey"]["destinationStation"] = os.getenv("destinationStation") or ""
    if data["journey"]["destinationStation"] and data["journey"]["destinationStation"] not in ("null", "undefined"):
        data["journey"]["destinationStation"] = [s.strip() for s in data["journey"]["destinationStation"].split(",")]
    else:
        data["journey"]["destinationStation"] = [""]

    data["journey"]["individualStationDepartureTime"] = False
    if os.getenv("individualStationDepartureTime", "").upper() == "TRUE":
        data["journey"]["individualStationDepartureTime"] = True

    data["journey"]["outOfHoursName"] = os.getenv("outOfHoursName") or "London Paddington"
    data["journey"]["stationAbbr"] = {"International": "Intl."}
    data["journey"]['timeOffset'] = os.getenv("timeOffset") or "0"
    data["journey"]["screen1Platform"] = parsePlatformData(os.getenv("screen1Platform"))
    data["journey"]["screen2Platform"] = parsePlatformData(os.getenv("screen2Platform"))
    data["journey"]["screen1PlatformSchedule"] = parsePlatformSchedule(os.getenv("screen1PlatformSchedule") or "")
    data["journey"]["screen2PlatformSchedule"] = parsePlatformSchedule(os.getenv("screen2PlatformSchedule") or "")
    data["journey"]["platformScheduleWeekdayOnly"] = os.getenv("platformScheduleWeekdayOnly", "True").upper() != "FALSE"
    data["journey"]["numericPlatformsOnly"] = os.getenv("numericPlatformsOnly", "False").lower() == "true"
    
    data["api"]["apiKey"] = os.getenv("apiKey") or None
    data["api"]["operatingHours"] = os.getenv("operatingHours") or ""

    data["showDepartureNumbers"] = False
    if os.getenv("showDepartureNumbers", "").upper() == "TRUE":
        data["showDepartureNumbers"] = True

    data["testDisruptionMessage"] = os.getenv("testDisruptionMessage") or ""
    data["minsThreshold"] = int(os.getenv("minsThreshold") or 20)

    validateConfig(data)
    return data


def validateConfig(data):
    if data["refreshTime"] < 30:
        print(f'Warning: refreshTime is {data["refreshTime"]}s which may cause API rate limiting')

    if data["api"]["apiKey"] is None:
        print("Warning: apiKey is not set - API calls will fail")

    for screen in ("screen1", "screen2"):
        envVal = os.getenv(f"{screen}PlatformSchedule") or ""
        if envVal and not data["journey"][f"{screen}PlatformSchedule"]:
            print(f'Warning: {screen}PlatformSchedule is set but could not be parsed - check format HH:MM-HH:MM=platform')

    if os.getenv("operatingHours") and not data['hoursPattern'].match(os.getenv("operatingHours")):
        print(f'Warning: operatingHours value "{os.getenv("operatingHours")}" is invalid - expected format HH-HH')

    if os.getenv("screenBlankHours") and not data['hoursPattern'].match(os.getenv("screenBlankHours")):
        print(f'Warning: screenBlankHours value "{os.getenv("screenBlankHours")}" is invalid - expected format HH-HH')

    crs = data["journey"]["departureStation"]
    if not re.match(r'^[A-Z]{3}$', crs):
        print(f'Warning: departureStation "{crs}" does not look like a valid CRS code (expected 3 uppercase letters)')
