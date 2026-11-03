from apis_externas_4.cli import build_parser


def test_cli_registers_three_challenge_groups():
    parser = build_parser()
    parsed = parser.parse_args(["flights", "track", "--icao24", "abc123"])
    assert parsed.challenge == "flights"
    assert parsed.command == "track"
    assert parsed.icao24 == "abc123"


def test_space_asteroids_requires_date_range():
    parser = build_parser()
    parsed = parser.parse_args([
        "space", "asteroids", "--start-date", "2025-01-01", "--end-date", "2025-01-02"
    ])
    assert parsed.start_date == "2025-01-01"
    assert parsed.end_date == "2025-01-02"
