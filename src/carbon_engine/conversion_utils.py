"""
conversion_utils.py
===================
Unit converters for the carbon engine.
"""

class UnitConverter:
    """Static utility methods for unit conversion."""
    
    MILES_TO_KM = 1.60934
    POUNDS_TO_KG = 0.453592
    GALLONS_TO_LITERS = 3.78541
    SHORT_TON_TO_METRIC_TON = 0.907185
    KWH_TO_MJ = 3.6
    
    @staticmethod
    def miles_to_km(miles: float) -> float:
        return miles * UnitConverter.MILES_TO_KM

    @staticmethod
    def km_to_miles(km: float) -> float:
        return km / UnitConverter.MILES_TO_KM

    @staticmethod
    def pounds_to_kg(lbs: float) -> float:
        return lbs * UnitConverter.POUNDS_TO_KG

    @staticmethod
    def kg_to_pounds(kg: float) -> float:
        return kg / UnitConverter.POUNDS_TO_KG
        
    @staticmethod
    def gallons_to_liters(gallons: float) -> float:
        return gallons * UnitConverter.GALLONS_TO_LITERS
        
    @staticmethod
    def liters_to_gallons(liters: float) -> float:
        return liters / UnitConverter.GALLONS_TO_LITERS

    @staticmethod
    def short_tons_to_metric_tons(short_tons: float) -> float:
        return short_tons * UnitConverter.SHORT_TON_TO_METRIC_TON
        
    @staticmethod
    def metric_tons_to_short_tons(metric_tons: float) -> float:
        return metric_tons / UnitConverter.SHORT_TON_TO_METRIC_TON

    @staticmethod
    def kwh_to_mj(kwh: float) -> float:
        return kwh * UnitConverter.KWH_TO_MJ

    @staticmethod
    def mj_to_kwh(mj: float) -> float:
        return mj / UnitConverter.KWH_TO_MJ

    @staticmethod
    def calculate_co2e(co2: float = 0.0, ch4: float = 0.0, n2o: float = 0.0, ch4_is_biogenic: bool = False) -> float:
        """
        Calculate CO2e from separate greenhouse gases using AR6 GWP100 constants.
        
        Parameters
        ----------
        co2: Mass of CO2 (e.g. kg)
        ch4: Mass of CH4 (e.g. kg)
        n2o: Mass of N2O (e.g. kg)
        ch4_is_biogenic: True if CH4 is biogenic, False if fossil
        """
        from .schemas import GWP_CO2, GWP_CH4_FOSSIL, GWP_CH4_BIOGENIC, GWP_N2O
        
        ch4_gwp = GWP_CH4_BIOGENIC if ch4_is_biogenic else GWP_CH4_FOSSIL
        
        return (co2 * GWP_CO2) + (ch4 * ch4_gwp) + (n2o * GWP_N2O)
