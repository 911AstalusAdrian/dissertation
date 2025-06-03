from datetime import timedelta

def format_laptime(td:timedelta) -> str:
    total_seconds = int(td.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    milliseconds = int(td.microseconds / 1000)

    return f'{minutes}:{seconds:02d}:{milliseconds:03d}'