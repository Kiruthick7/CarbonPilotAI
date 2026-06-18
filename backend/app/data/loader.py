"""Singleton data loader for static reference files.

``EmissionFactorLoader`` reads the three JSON data files at import time and
exposes typed accessor methods. The singleton is instantiated once per process
via the module-level ``_loader`` instance and exposed through ``get_loader()``.

Data files live in the same directory as this module (``app/data/``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import structlog

log: structlog.BoundLogger = structlog.get_logger(__name__)

_DATA_DIR = Path(__file__).parent

_GLOBAL_AVERAGE_GRID_INTENSITY = 0.490
_GLOBAL_AVERAGE_NATIONAL_TCO2E = 4.8


class EmissionFactorLoader:
    """Loads and validates emission-factor reference data at startup.

    Raises:
        ValueError: If any JSON file is missing required top-level keys.
        FileNotFoundError: If a data file does not exist on disk.
    """

    def __init__(self) -> None:
        """Load all three data files and validate their structure."""
        self._factors: dict[str, Any] = self._load_and_validate(
            _DATA_DIR / "emission_factors.json",
            required_keys={"version", "transport", "diet", "home", "consumption"},
        )
        self._grid: dict[str, Any] = self._load_and_validate(
            _DATA_DIR / "country_grid.json",
            required_keys={"version", "countries", "global_average_grid_intensity"},
        )
        self._benchmarks: dict[str, Any] = self._load_and_validate(
            _DATA_DIR / "benchmarks.json",
            required_keys={"budget_1_5c_tco2e_per_person", "global_average_tco2e"},
        )
        log.info(
            "emission_factor_loader.ready",
            factors_version=self._factors.get("version"),
            grid_version=self._grid.get("version"),
            benchmarks_version=self._benchmarks.get("version"),
            country_count=len(self._grid.get("countries", {})),
        )





    @staticmethod
    def _load_and_validate(path: Path, required_keys: set[str]) -> dict[str, Any]:
        """Read and JSON-parse a file, then verify required top-level keys.

        Args:
            path: Absolute path to the JSON file.
            required_keys: Set of keys that must exist at the top level.

        Returns:
            Parsed JSON as a dict.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If any required key is absent.
        """
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")

        with path.open(encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)

        missing = required_keys - set(data.keys())
        if missing:
            raise ValueError(
                f"Data file {path.name!r} is missing required keys: {sorted(missing)}"
            )

        return data





    def get_factors(self) -> dict[str, Any]:
        """Return the full emission-factors dictionary.

        Returns:
            Deep dict of emission factor data keyed by category and sub-category.
        """
        return self._factors

    def get_grid_intensity(self, country_code: str) -> float:
        """Return the grid carbon intensity for a country in kgCO2e/kWh.

        Falls back to the global average if the country code is not found.

        Args:
            country_code: ISO 3166-1 alpha-2 code (upper-case, e.g. ``"GB"``).

        Returns:
            Grid intensity in kgCO2e/kWh.
        """
        countries: dict[str, Any] = self._grid.get("countries", {})
        country_data = countries.get(country_code.upper())
        if country_data is None:
            log.warning(
                "emission_factor_loader.country_not_found",
                country_code=country_code,
                fallback=_GLOBAL_AVERAGE_GRID_INTENSITY,
            )
            return float(self._grid.get("global_average_grid_intensity", _GLOBAL_AVERAGE_GRID_INTENSITY))

        return float(country_data["grid_intensity"])

    def get_national_average(self, country_code: str) -> float:
        """Return the national per-person average annual emissions in tCO2e.

        Falls back to the global average if the country code is not found.

        Args:
            country_code: ISO 3166-1 alpha-2 code (upper-case).

        Returns:
            National average in tCO2e per person per year.
        """
        countries: dict[str, Any] = self._grid.get("countries", {})
        country_data = countries.get(country_code.upper())
        if country_data is None:
            log.warning(
                "emission_factor_loader.national_avg_not_found",
                country_code=country_code,
                fallback=_GLOBAL_AVERAGE_NATIONAL_TCO2E,
            )
            return _GLOBAL_AVERAGE_NATIONAL_TCO2E

        return float(country_data["national_avg_tco2e"])

    def get_benchmarks(self) -> dict[str, Any]:
        """Return the full benchmarks dictionary.

        Returns:
            Dict containing 1.5°C budget, global averages, and equivalences.
        """
        return self._benchmarks

    @property
    def factors(self) -> dict[str, Any]:
        """Property access to emission factors."""
        return self._factors

    @property
    def grid_intensity(self) -> dict[str, float]:
        """Property access to country grid intensities as a dictionary."""
        countries = self._grid.get("countries", {})
        return {k: float(v["grid_intensity"]) for k, v in countries.items()}

    @property
    def benchmarks(self) -> dict[str, Any]:
        """Property access to benchmarks."""
        return self._benchmarks






def get_loader() -> EmissionFactorLoader:
    """Return the process-level singleton ``EmissionFactorLoader``.

    The loader is created lazily on first call and cached for subsequent calls.
    This avoids repeated disk I/O and JSON parsing.

    Returns:
        The singleton ``EmissionFactorLoader`` instance.

    Raises:
        FileNotFoundError: If a required data file is missing.
        ValueError: If a data file is structurally invalid.
    """
    global _loader
    if _loader is None:
        _loader = EmissionFactorLoader()
    return _loader


_loader: EmissionFactorLoader | None = None
