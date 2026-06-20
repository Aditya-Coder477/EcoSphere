"""
factor_lookup.py
================
Singleton factor lookup class that lazily loads all emission factor tables.
"""

import pandas as pd
from typing import Dict, Optional, Any, Tuple
from pathlib import Path

from config import CFG
from src.utils.logger import get_logger
from .exceptions import MissingCountryDataError

logger = get_logger(__name__)


class EmissionFactorLookup:
    """
    Lazily loads and provides access to emission factors from cleaned datasets.
    Designed as a singleton to avoid repeated file I/O.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmissionFactorLookup, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._transport_factors: Optional[pd.DataFrame] = None
        self._food_factors: Optional[pd.DataFrame] = None
        self._electricity_mix: Optional[pd.DataFrame] = None
        self._waste_factors: Optional[pd.DataFrame] = None
        self._cleaned_dir = Path(CFG.CLEANED_DIR)
        
        self._initialized = True

    def _load_csv_safe(self, filename: str) -> Optional[pd.DataFrame]:
        filepath = self._cleaned_dir / filename
        if not filepath.exists():
            logger.warning(f"FactorLookup: Missing dataset {filepath}")
            return None
        try:
            return pd.read_csv(filepath)
        except Exception as e:
            logger.error(f"FactorLookup: Failed to read {filename} - {e}")
            return None

    def _ensure_transport(self):
        if self._transport_factors is None:
            self._transport_factors = self._load_csv_safe("transport_factors.csv")

    def _ensure_food(self):
        if self._food_factors is None:
            self._food_factors = self._load_csv_safe("food_ghg_factors.csv")

    def _ensure_electricity(self):
        if self._electricity_mix is None:
            self._electricity_mix = self._load_csv_safe("electricity_mix.csv")

    def _ensure_waste(self):
        if self._waste_factors is None:
            self._waste_factors = self._load_csv_safe("waste.csv")

    # --- Transport ---

    def get_transport_factor(self, mode: str) -> Optional[Tuple[float, str]]:
        """
        Returns (factor_value, unit) for a given transport mode.
        If mode is not found, returns None.
        """
        self._ensure_transport()
        if self._transport_factors is None or self._transport_factors.empty:
            return None

        # Clean string matching
        mode_clean = mode.strip().lower()
        
        # Match case-insensitively
        match = self._transport_factors[self._transport_factors['mode'].str.strip().str.lower() == mode_clean]
        
        if match.empty:
            return None
            
        row = match.iloc[0]
        return float(row['co2e_kg_per_unit']), str(row['unit'])

    # --- Food ---

    def get_food_factor(self, food_item: str) -> Optional[float]:
        """
        Returns emission factor (kg CO2e per kg) for a food item.
        Returns None if not found.
        """
        self._ensure_food()
        if self._food_factors is None or self._food_factors.empty:
            return None

        item_clean = food_item.strip().lower()
        match = self._food_factors[self._food_factors['entity'].str.strip().str.lower() == item_clean]
        
        if match.empty:
            return None
            
        return float(match.iloc[0]['greenhouse_gas_emissions_per_kilogram'])

    # --- Electricity ---

    def get_electricity_grid_intensity(self, country: str, year: Optional[int] = None) -> Optional[float]:
        """
        Returns grid intensity (kg CO2 per kWh) for a country and optionally a specific year.
        If year is not provided, defaults to the most recent year available for the country.
        """
        self._ensure_electricity()
        if self._electricity_mix is None or self._electricity_mix.empty:
            return None

        country_clean = country.strip().lower()
        country_data = self._electricity_mix[self._electricity_mix['country'].str.strip().str.lower() == country_clean]
        
        if country_data.empty:
            return None
            
        if year is not None:
            year_data = country_data[country_data['year'] == year]
            if not year_data.empty:
                return float(year_data.iloc[0]['grid_intensity_kg_co2_per_kwh'])
        
        # Fallback to most recent year for that country
        most_recent = country_data.sort_values(by='year', ascending=False).iloc[0]
        return float(most_recent['grid_intensity_kg_co2_per_kwh'])

    def get_electricity_country_average_kwh(self, country: str) -> Optional[float]:
        """
        Returns the average annual per-capita energy/electricity usage (kWh).
        Since our main electricity dataset only has mix/intensity, we can either
        derive it from a merged dataset or rely on the caller/calculator to use regional fallbacks.
        (ElectricityCalculator handles regional fallback if this returns None).
        """
        # For now, return None and let ElectricityCalculator handle the regional fallback
        return None

    # --- Waste ---

    def get_waste_factors(self, country: str, year: Optional[int] = None) -> Optional[Dict[str, float]]:
        """
        Returns a dictionary with waste_generated_kg_per_capita_per_day, landfill_rate_pct, 
        and estimated_waste_emissions_kg_co2e_per_kg_waste.
        """
        self._ensure_waste()
        if self._waste_factors is None or self._waste_factors.empty:
            return None

        country_clean = country.strip().lower()
        country_data = self._waste_factors[self._waste_factors['country'].str.strip().str.lower() == country_clean]
        
        if country_data.empty:
            return None
            
        if year is not None:
            year_data = country_data[country_data['year'] == year]
            if not year_data.empty:
                row = year_data.iloc[0]
                return {
                    "waste_generated_kg_per_capita_per_day": float(row['waste_generated_kg_per_capita_per_day']),
                    "landfill_rate_pct": float(row['landfill_rate_pct']),
                    "emission_factor": float(row['estimated_waste_emissions_kg_co2e_per_kg_waste'])
                }

        # Fallback to most recent year
        row = country_data.sort_values(by='year', ascending=False).iloc[0]
        return {
            "waste_generated_kg_per_capita_per_day": float(row['waste_generated_kg_per_capita_per_day']),
            "landfill_rate_pct": float(row['landfill_rate_pct']),
            "emission_factor": float(row['estimated_waste_emissions_kg_co2e_per_kg_waste'])
        }

