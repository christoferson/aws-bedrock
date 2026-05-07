import pytest
from tools.converter import unit_converter


class TestUnitConverterTemperature:
    def test_celsius_to_fahrenheit(self):
        result = unit_converter(0, "celsius", "fahrenheit")
        assert result == 32.0

        result = unit_converter(100, "celsius", "fahrenheit")
        assert result == 212.0

    def test_fahrenheit_to_celsius(self):
        result = unit_converter(32, "fahrenheit", "celsius")
        assert result == 0.0

        result = unit_converter(212, "fahrenheit", "celsius")
        assert result == 100.0

    def test_celsius_to_kelvin(self):
        result = unit_converter(0, "celsius", "kelvin")
        assert result == 273.15

        result = unit_converter(100, "celsius", "kelvin")
        assert result == 373.15

    def test_kelvin_to_celsius(self):
        result = unit_converter(273.15, "kelvin", "celsius")
        assert abs(result - 0.0) < 0.001

    def test_identity_conversion(self):
        result = unit_converter(25, "celsius", "celsius")
        assert result == 25.0


class TestUnitConverterLength:
    def test_meters_to_feet(self):
        result = unit_converter(1, "meters", "feet")
        assert abs(result - 3.28084) < 0.001

    def test_feet_to_meters(self):
        result = unit_converter(3.28084, "feet", "meters")
        assert abs(result - 1.0) < 0.001

    def test_miles_to_kilometers(self):
        result = unit_converter(1, "miles", "kilometers")
        assert abs(result - 1.609344) < 0.001

        result = unit_converter(5, "miles", "kilometers")
        assert abs(result - 8.04672) < 0.001

    def test_kilometers_to_miles(self):
        result = unit_converter(1.609344, "kilometers", "miles")
        assert abs(result - 1.0) < 0.001

    def test_inches_to_centimeters(self):
        result = unit_converter(1, "inches", "centimeters")
        assert abs(result - 2.54) < 0.001

    def test_centimeters_to_inches(self):
        result = unit_converter(2.54, "centimeters", "inches")
        assert abs(result - 1.0) < 0.001


class TestUnitConverterWeight:
    def test_pounds_to_kilograms(self):
        result = unit_converter(1, "pounds", "kilograms")
        assert abs(result - 0.453592) < 0.001

        result = unit_converter(150, "pounds", "kilograms")
        assert abs(result - 68.0389) < 0.01

    def test_kilograms_to_pounds(self):
        result = unit_converter(1, "kilograms", "pounds")
        assert abs(result - 2.20462) < 0.001

    def test_kilograms_to_grams(self):
        result = unit_converter(1, "kilograms", "grams")
        assert result == 1000.0

    def test_grams_to_kilograms(self):
        result = unit_converter(1000, "grams", "kilograms")
        assert result == 1.0

    def test_ounces_to_grams(self):
        result = unit_converter(1, "ounces", "grams")
        assert abs(result - 28.3495) < 0.001


class TestUnitConverterVolume:
    def test_gallons_to_liters(self):
        result = unit_converter(1, "gallons", "liters")
        assert abs(result - 3.78541) < 0.001

        result = unit_converter(2, "gallons", "liters")
        assert abs(result - 7.57082) < 0.001

    def test_liters_to_gallons(self):
        result = unit_converter(3.78541, "liters", "gallons")
        assert abs(result - 1.0) < 0.001

    def test_liters_to_milliliters(self):
        result = unit_converter(1, "liters", "milliliters")
        assert result == 1000.0

    def test_milliliters_to_liters(self):
        result = unit_converter(1000, "milliliters", "liters")
        assert result == 1.0

    def test_cups_to_liters(self):
        result = unit_converter(1, "cups", "liters")
        assert abs(result - 0.236588) < 0.001


class TestUnitConverterAliases:
    def test_temperature_aliases(self):
        result = unit_converter(0, "c", "f")
        assert result == 32.0

        result = unit_converter(0, "celsius", "k")
        assert result == 273.15

    def test_length_aliases(self):
        result = unit_converter(1, "m", "ft")
        assert abs(result - 3.28084) < 0.001

        result = unit_converter(1, "km", "mi")
        assert abs(result - 0.621371) < 0.001

    def test_weight_aliases(self):
        result = unit_converter(1, "kg", "lb")
        assert abs(result - 2.20462) < 0.001

        result = unit_converter(1, "g", "oz")
        assert abs(result - 0.035274) < 0.001

    def test_volume_aliases(self):
        result = unit_converter(1, "l", "gal")
        assert abs(result - 0.264172) < 0.001


class TestUnitConverterCaseInsensitivity:
    def test_uppercase_units(self):
        result = unit_converter(100, "CELSIUS", "FAHRENHEIT")
        assert result == 212.0

    def test_mixed_case_units(self):
        result = unit_converter(1, "Meters", "Feet")
        assert abs(result - 3.28084) < 0.001


class TestUnitConverterErrors:
    def test_unsupported_from_unit(self):
        with pytest.raises(ValueError, match="Unsupported unit 'parsecs'"):
            unit_converter(1, "parsecs", "meters")

    def test_unsupported_to_unit(self):
        with pytest.raises(ValueError, match="Unsupported unit 'furlongs'"):
            unit_converter(1, "meters", "furlongs")

    def test_incompatible_unit_types(self):
        with pytest.raises(ValueError, match="Cannot convert between different unit types"):
            unit_converter(100, "celsius", "meters")

        with pytest.raises(ValueError, match="Cannot convert between different unit types"):
            unit_converter(5, "pounds", "liters")

        with pytest.raises(ValueError, match="Cannot convert between different unit types"):
            unit_converter(10, "kilometers", "gallons")
