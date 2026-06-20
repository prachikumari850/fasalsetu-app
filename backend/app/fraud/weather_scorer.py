from __future__ import annotations
import uuid
from datetime import date, timedelta
import httpx
from app.models.claim import DamageType
from app.core.config import settings
import structlog

logger = structlog.get_logger()

MAX_SCORE = 20.0

# Weather conditions that support each damage type
DAMAGE_WEATHER_MAP = {
    DamageType.drought: {
        "check": "no_rain",
        "description": "Low rainfall (< 1mm/day) for extended period",
    },
    DamageType.flood: {
        "check": "heavy_rain",
        "description": "Heavy rainfall (> 25mm/day)",
    },
    DamageType.hail: {
        "check": "precipitation",
        "description": "Significant precipitation event",
    },
    DamageType.pest: {
        "check": "warm_humid",
        "description": "Warm and humid conditions favour pest activity",
    },
    DamageType.disease: {
        "check": "warm_humid",
        "description": "Warm and humid conditions favour disease spread",
    },
    DamageType.fire: {
        "check": "hot_dry",
        "description": "Hot and dry conditions that could support fire",
    },
    DamageType.other: {
        "check": "any",
        "description": "No specific weather condition required",
    },
}


async def fetch_weather_data(
    lat: float,
    lng: float,
    start_date: date,
    end_date: date,
) -> dict | None:
    """
    Fetch historical weather from Open-Meteo API.
    Free, no API key required.
    """
    url = f"{settings.open_meteo_base_url}/archive"
    params = {
        "latitude":   lat,
        "longitude":  lng,
        "start_date": start_date.isoformat(),
        "end_date":   end_date.isoformat(),
        "daily": [
            "precipitation_sum",
            "temperature_2m_max",
            "temperature_2m_min",
            "windspeed_10m_max",
            "relative_humidity_2m_max",
        ],
        "timezone": "Asia/Kolkata",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        logger.warning("Open-Meteo timeout", lat=lat, lng=lng)
        return None
    except Exception as e:
        logger.error("Open-Meteo fetch failed", error=str(e))
        return None


def _check_weather_supports_damage(
    weather_data: dict,
    damage_type: DamageType,
) -> tuple[bool, str]:
    """
    Check if weather conditions are consistent with the claimed damage type.
    Returns (supports_claim, explanation).
    """
    daily  = weather_data.get("daily", {})
    precip = daily.get("precipitation_sum", [])
    temp_max = daily.get("temperature_2m_max", [])
    temp_min = daily.get("temperature_2m_min", [])
    humidity = daily.get("relative_humidity_2m_max", [])

    check = DAMAGE_WEATHER_MAP.get(damage_type, {}).get("check", "any")

    if check == "any":
        return True, "No specific weather condition required for this damage type."

    if check == "no_rain":
        # Drought: average precipitation < 1mm/day for the period
        if precip:
            avg_precip = sum(precip) / len(precip)
            if avg_precip < 1.0:
                return True, f"Low average precipitation ({avg_precip:.1f}mm/day) consistent with drought."
            return False, f"Average precipitation {avg_precip:.1f}mm/day — insufficient for drought claim."

    if check == "heavy_rain":
        # Flood: at least one day with > 25mm rainfall
        if precip:
            max_precip = max(precip)
            if max_precip >= 25.0:
                return True, f"Heavy rainfall recorded ({max_precip:.1f}mm) — consistent with flood."
            return False, f"Max daily rainfall {max_precip:.1f}mm — insufficient for flood claim."

    if check == "precipitation":
        # Hail: any significant precipitation event
        if precip:
            max_precip = max(precip)
            if max_precip >= 5.0:
                return True, f"Precipitation event ({max_precip:.1f}mm) — possible hail conditions."
            return False, f"No significant precipitation event for hail claim."

    if check == "warm_humid":
        # Pest/disease: warm (>25°C) AND humid (>70%)
        if temp_max and humidity:
            avg_temp = sum(temp_max) / len(temp_max)
            avg_humid = sum(h for h in humidity if h) / max(len(humidity), 1)
            if avg_temp >= 25.0 and avg_humid >= 60.0:
                return True, (
                    f"Warm ({avg_temp:.1f}°C) and humid ({avg_humid:.0f}%) conditions "
                    "favour pest/disease activity."
                )
            return False, (
                f"Temperature ({avg_temp:.1f}°C) and humidity ({avg_humid:.0f}%) "
                "do not strongly support pest/disease conditions."
            )

    if check == "hot_dry":
        # Fire: hot (>35°C) AND dry (<5mm total precipitation)
        if temp_max and precip:
            max_temp  = max(temp_max)
            total_precip = sum(precip)
            if max_temp >= 35.0 and total_precip < 5.0:
                return True, f"Hot ({max_temp:.1f}°C) and dry ({total_precip:.1f}mm) — fire-prone conditions."
            return False, f"Conditions not consistent with fire claim."

    return True, "Weather data inconclusive — giving benefit of doubt."


async def score_weather_validation(
    lat: float,
    lng: float,
    damage_type: DamageType,
    damage_date: date,
) -> tuple[float, list[str], dict | None]:
    """
    Validate weather conditions against claimed damage type.
    Checks the 7-day window ending on the damage date.

    Returns (score, flags, weather_data)
    """
    flags: list[str] = []

    # Fetch 7-day window ending on damage date
    end_date   = damage_date
    start_date = damage_date - timedelta(days=7)

    weather_data = await fetch_weather_data(lat, lng, start_date, end_date)

    if weather_data is None:
        # Cannot validate — give partial score (benefit of doubt)
        flags.append("WEATHER_DATA_UNAVAILABLE: Could not fetch historical weather data")
        return MAX_SCORE * 0.6, flags, None

    supported, explanation = _check_weather_supports_damage(weather_data, damage_type)

    if supported:
        score = MAX_SCORE
    else:
        score = 0.0
        flags.append(
            f"WEATHER_MISMATCH: {explanation} "
            f"Claimed damage: {damage_type.value}"
        )

    logger.info(
        "Weather validation scored",
        score=score,
        damage_type=damage_type.value,
        supported=supported,
    )

    return score, flags, weather_data