from __future__ import annotations

from dataclasses import dataclass


AIRCRAFT_CATEGORIES = {
    0: "Sem informação",
    1: "Categoria ADS-B desconhecida",
    2: "Leve",
    3: "Pequeno",
    4: "Grande",
    5: "Grande - alto vórtice",
    6: "Pesado",
    7: "Alto desempenho",
    8: "Helicóptero",
    9: "Planador",
    10: "Balão / dirigível",
    11: "Paraquedista",
    12: "Ultraleve",
    13: "Reservado",
    14: "Veículo aéreo não tripulado",
    15: "Espacial / transatmosférico",
    16: "Veículo de emergência em superfície",
    17: "Veículo de serviço em superfície",
    18: "Obstáculo pontual",
    19: "Obstáculo agrupado",
    20: "Obstáculo linear",
}


@dataclass(frozen=True, slots=True)
class BoundingBox:
    lamin: float
    lomin: float
    lamax: float
    lomax: float

    def __post_init__(self) -> None:
        if not -90 <= self.lamin <= 90 or not -90 <= self.lamax <= 90:
            raise ValueError("Latitudes devem estar entre -90 e 90 graus.")
        if not -180 <= self.lomin <= 180 or not -180 <= self.lomax <= 180:
            raise ValueError("Longitudes devem estar entre -180 e 180 graus.")
        if self.lamin >= self.lamax or self.lomin >= self.lomax:
            raise ValueError("Bounding box inválida: os limites mínimos devem ser menores que os máximos.")

    def to_params(self) -> dict[str, float]:
        return {
            "lamin": self.lamin,
            "lomin": self.lomin,
            "lamax": self.lamax,
            "lomax": self.lomax,
        }


# Caixa geográfica aproximada para cobrir o território continental brasileiro.
# Como é um retângulo, também pode incluir áreas marítimas e pequenas áreas de países vizinhos.
BRAZIL_BBOX = BoundingBox(lamin=-33.75, lomin=-73.99, lamax=5.27, lomax=-34.79)


@dataclass(frozen=True, slots=True)
class AircraftPosition:
    icao24: str
    callsign: str | None
    origin_country: str | None
    time_position: int | None
    last_contact: int | None
    longitude: float | None
    latitude: float | None
    baro_altitude_m: float | None
    on_ground: bool | None
    velocity_m_s: float | None
    true_track_deg: float | None
    vertical_rate_m_s: float | None
    geo_altitude_m: float | None
    squawk: str | None
    position_source: int | None
    category: int | None

    @property
    def category_name(self) -> str:
        if self.category is None:
            return "Não informada"
        return AIRCRAFT_CATEGORIES.get(self.category, f"Categoria {self.category}")


@dataclass(frozen=True, slots=True)
class FlightWaypoint:
    timestamp: int
    latitude: float | None
    longitude: float | None
    baro_altitude_m: float | None
    true_track_deg: float | None
    on_ground: bool | None


@dataclass(frozen=True, slots=True)
class FlightTrack:
    icao24: str
    start_time: int | None
    end_time: int | None
    callsign: str | None
    path: tuple[FlightWaypoint, ...]


@dataclass(frozen=True, slots=True)
class AirportFlight:
    icao24: str
    first_seen: int | None
    last_seen: int | None
    callsign: str | None
    est_departure_airport: str | None
    est_arrival_airport: str | None
    departure_airport_candidates: int | None = None
    arrival_airport_candidates: int | None = None
