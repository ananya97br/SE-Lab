def parse_ride_duration(text):
    """
    Converts a ride duration written as HH:MM into minutes.
    Returns None if the input is not a valid HH:MM string.
    """
    if not isinstance(text, str):
        return None

    text = text.strip()
    if len(text) > 20:  # avoids huge-integer conversion problems
        return None

    parts = text.split(':')
    if len(parts) != 2:  # no colon, or more than one colon
        return None

    hours, minutes = parts[0].strip(), parts[1].strip()
    if not (hours.isdecimal() and minutes.isdecimal()):
        return None

    hours, minutes = int(hours), int(minutes)
    if minutes >= 60:
        return None

    return hours * 60 + minutes


def format_station_code(code):
    """
    Formats a station code as ZONE-NUMBER, e.g. 'a12' -> 'A-12'.
    Returns None if the code is not a string or is too short.
    """
    if not isinstance(code, str):
        return None

    code = code.strip().upper()
    if len(code) < 2:  # need at least a zone and a number
        return None

    return code[0] + '-' + code[1:]


def parse_ride_log(line):
    """
    Parses 'bike_type,minutes,subscriber' into a tuple.
    Returns None if the line is malformed.
    """
    if not isinstance(line, str):
        return None

    parts = line.split(',')
    if len(parts) != 3:  # missing or extra fields
        return None

    bike_type = parts[0].strip()
    minutes = parts[1].strip()
    subscriber = parts[2].strip().lower()

    if not bike_type:
        return None
    if not minutes.isdecimal() or len(minutes) > 9:
        return None

    return bike_type, int(minutes), subscriber == 'yes'


def main():
    print("==== Running parse_ride_duration ====")
    value = input("Enter a ride duration as HH:MM (e.g. 01:15): ")
    result = parse_ride_duration(value)
    if result is None:
        print("Invalid input: expected HH:MM (e.g. 01:15)")
    else:
        print("Duration in minutes:", result)

    print("\n==== Running format_station_code ====")
    value = input("Enter a station code (e.g. a12): ")
    result = format_station_code(value)
    if result is None:
        print("Invalid input: station code needs at least 2 characters")
    else:
        print("Formatted station code:", result)

    print("\n==== Running parse_ride_log ====")
    value = input("Enter a ride log line as type,minutes,subscriber (e.g. electric,45,yes): ")
    result = parse_ride_log(value)
    if result is None:
        print("Invalid input: expected type,minutes,subscriber (e.g. electric,45,yes)")
    else:
        print("Parsed ride log:", result)


if __name__ == "__main__":
    main()