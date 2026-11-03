from __future__ import annotations

from datetime import UTC, datetime

from apis_externas_4.challenges.flight_tracking.domain.models import AirportFlight


def format_airport_flights(flights: list[AirportFlight]) -> str:
    if not flights:
        return "Nenhum voo encontrado no intervalo consultado."
    rows = []
    for item in flights:
        seen = datetime.fromtimestamp(item.first_seen, UTC).strftime("%Y-%m-%d %H:%M UTC") if item.first_seen else "N/D"
        rows.append((item.icao24, item.callsign or "N/D", item.est_departure_airport or "N/D", item.est_arrival_airport or "N/D", seen))
    headers = ("ICAO24", "CALLSIGN", "ORIGEM", "DESTINO", "PRIMEIRO SINAL")
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    lines = ["  ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend("  ".join(row[i].ljust(widths[i]) for i in range(len(headers))) for row in rows)
    return "\n".join(lines)
