"""Astronomical calculation module for 月相羅針 PoC v0.1.

This module is intentionally separated from the proprietary 月相羅針
classification logic.  It converts a local birth time to UTC and calculates
geocentric tropical longitudes of the Sun and Moon with pyswisseph.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import swisseph as swe


class AstronomyError(RuntimeError):
    """Raised when an astronomical calculation cannot be completed."""


def normalize_angle(angle: float) -> float:
    """Normalize an angle to the range 0 <= angle < 360 degrees."""
    return float(angle) % 360.0


def local_datetime_to_utc(
    birth_date: str,
    birth_time: str,
    timezone_name: str,
) -> tuple[datetime, datetime]:
    """Parse local birth date/time and convert it to UTC.

    Parameters are strings from the HTML date/time inputs (YYYY-MM-DD, HH:MM)
    and an IANA time-zone name such as Asia/Tokyo.
    """
    try:
        local_naive = datetime.strptime(
            f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M"
        )
    except ValueError as exc:
        raise ValueError("生年月日または出生時間の形式が正しくありません。") from exc

    try:
        tz = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError("指定されたタイムゾーンを利用できません。") from exc

    local_dt = local_naive.replace(tzinfo=tz)
    utc_dt = local_dt.astimezone(timezone.utc)
    return local_dt, utc_dt


def datetime_utc_to_julian_day(utc_dt: datetime) -> float:
    """Convert a timezone-aware UTC datetime to Julian Day (UT)."""
    if utc_dt.tzinfo is None:
        raise ValueError("UTC日時にはタイムゾーン情報が必要です。")

    utc_dt = utc_dt.astimezone(timezone.utc)
    decimal_hour = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3_600_000_000.0
    )
    return swe.julday(
        utc_dt.year,
        utc_dt.month,
        utc_dt.day,
        decimal_hour,
        swe.GREG_CAL,
    )


def _ephemeris_mode_label(return_flags: int) -> str:
    """Return a human-readable label for the ephemeris actually used."""
    if return_flags & swe.FLG_JPLEPH:
        return "JPL ephemeris via Swiss Ephemeris"
    if return_flags & swe.FLG_SWIEPH:
        return "Swiss Ephemeris"
    if return_flags & swe.FLG_MOSEPH:
        return "Moshier fallback via Swiss Ephemeris"
    return "Swiss Ephemeris / pyswisseph"


def calculate_longitudes(julian_day_ut: float) -> dict[str, float | str]:
    """Calculate geocentric tropical Sun/Moon ecliptic longitudes.

    No sidereal flag and no topocentric flag are set, so the result is the
    default tropical, geocentric ecliptic longitude requested for this PoC.

    FLG_SWIEPH is requested.  If external Swiss Ephemeris data files are not
    present, the library may transparently fall back to its Moshier mode; this
    is reported in the returned metadata so the calculation method is visible.
    """
    try:
        requested_flags = swe.FLG_SWIEPH
        sun_data, sun_flags = swe.calc_ut(julian_day_ut, swe.SUN, requested_flags)
        moon_data, moon_flags = swe.calc_ut(julian_day_ut, swe.MOON, requested_flags)
    except Exception as exc:  # pyswisseph can raise several low-level errors
        raise AstronomyError("太陽・月の天体計算に失敗しました。") from exc

    sun_longitude = normalize_angle(sun_data[0])
    moon_longitude = normalize_angle(moon_data[0])
    angle_difference = normalize_angle(moon_longitude - sun_longitude)

    return {
        "sun_longitude": sun_longitude,
        "moon_longitude": moon_longitude,
        "angle_difference": angle_difference,
        "sun_ephemeris_mode": _ephemeris_mode_label(sun_flags),
        "moon_ephemeris_mode": _ephemeris_mode_label(moon_flags),
    }


def calculate_birth_astronomy(
    birth_date: str,
    birth_time: str,
    timezone_name: str,
) -> dict[str, object]:
    """Run the complete date/time and astronomy calculation pipeline."""
    local_dt, utc_dt = local_datetime_to_utc(
        birth_date=birth_date,
        birth_time=birth_time,
        timezone_name=timezone_name,
    )
    julian_day = datetime_utc_to_julian_day(utc_dt)
    values = calculate_longitudes(julian_day)

    return {
        "local_datetime": local_dt,
        "utc_datetime": utc_dt,
        "julian_day": julian_day,
        **values,
    }
