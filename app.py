"""Flask Web application for 月相羅針 計算PoC v0.1."""

from __future__ import annotations

import os
from datetime import datetime

from flask import Flask, render_template, request

from astronomy import AstronomyError, calculate_birth_astronomy
from location_master import resolve_location
from phase_classifier import classify_phase


app = Flask(__name__)


def _validate_form(birth_date: str, birth_time: str, birth_place: str) -> list[str]:
    errors: list[str] = []

    if not birth_date:
        errors.append("生年月日を入力してください。")
    else:
        try:
            datetime.strptime(birth_date, "%Y-%m-%d")
        except ValueError:
            errors.append("生年月日の形式が正しくありません。")

    if not birth_time:
        errors.append("出生時間を入力してください。")
    else:
        try:
            datetime.strptime(birth_time, "%H:%M")
        except ValueError:
            errors.append("出生時間の形式が正しくありません。")

    if not birth_place.strip():
        errors.append("出生地を入力してください。")

    return errors


@app.route("/", methods=["GET", "POST"])
def index():
    form = {
        "birth_date": "",
        "birth_time": "",
        "birth_place": "",
    }
    errors: list[str] = []
    result: dict[str, object] | None = None

    if request.method == "POST":
        form = {
            "birth_date": request.form.get("birth_date", "").strip(),
            "birth_time": request.form.get("birth_time", "").strip(),
            "birth_place": request.form.get("birth_place", "").strip(),
        }
        errors = _validate_form(**form)

        if not errors:
            try:
                location = resolve_location(form["birth_place"])
                astronomy = calculate_birth_astronomy(
                    birth_date=form["birth_date"],
                    birth_time=form["birth_time"],
                    timezone_name=str(location["timezone"]),
                )
                phase = classify_phase(float(astronomy["angle_difference"]))

                local_dt = astronomy["local_datetime"]
                utc_dt = astronomy["utc_datetime"]
                result = {
                    "birth_data": (
                        f'{local_dt.strftime("%Y-%m-%d %H:%M:%S")} '
                        f'{form["birth_place"]}'
                    ),
                    "timezone": location["timezone"],
                    "utc_datetime": utc_dt.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "julian_day": float(astronomy["julian_day"]),
                    "sun_longitude": float(astronomy["sun_longitude"]),
                    "moon_longitude": float(astronomy["moon_longitude"]),
                    "angle_difference": float(astronomy["angle_difference"]),
                    "phase_id": phase["id"],
                    "phase_name": phase["name"],
                    "phase_range": phase["range_text"],
                    "ephemeris_mode": astronomy["sun_ephemeris_mode"],
                }
            except ValueError as exc:
                errors.append(str(exc))
            except AstronomyError:
                app.logger.exception("Astronomy calculation failed")
                errors.append("天体計算に失敗しました。入力内容を確認して、もう一度お試しください。")
            except Exception:
                # Do not expose Python internals to the browser.
                app.logger.exception("Unexpected calculation error")
                errors.append("計算中にエラーが発生しました。もう一度お試しください。")

    return render_template(
        "index.html",
        form=form,
        errors=errors,
        result=result,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
