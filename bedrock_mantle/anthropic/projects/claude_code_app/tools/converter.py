from pydantic import Field


def unit_converter(
    value: float = Field(description="The numerical value to convert"),
    from_unit: str = Field(description="The unit to convert from (e.g., 'celsius', 'meters', 'pounds')"),
    to_unit: str = Field(description="The unit to convert to (e.g., 'fahrenheit', 'feet', 'kilograms')")
) -> float:
    """Convert values between different units of measurement.

    Supports conversions for temperature, length, weight/mass, and volume.
    All conversions are performed through a base unit for accuracy.

    Supported conversions:
    - Temperature: celsius, fahrenheit, kelvin
    - Length: meters, kilometers, miles, feet, inches, centimeters
    - Weight: kilograms, grams, pounds, ounces
    - Volume: liters, milliliters, gallons, cups

    When to use:
    - When you need to convert between units of measurement
    - When working with scientific or everyday unit conversions
    - When you need accurate conversion calculations

    When not to use:
    - For currency conversions (rates change frequently)
    - For complex unit conversions not listed above

    Examples:
    >>> unit_converter(100, "celsius", "fahrenheit")
    212.0
    >>> unit_converter(5, "miles", "kilometers")
    8.04672
    >>> unit_converter(150, "pounds", "kilograms")
    68.0389
    >>> unit_converter(2, "gallons", "liters")
    7.57082
    """
    # Normalize inputs to lowercase
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()

    # Unit aliases mapping to canonical names
    unit_aliases = {
        # Temperature
        'c': 'celsius',
        'f': 'fahrenheit',
        'k': 'kelvin',

        # Length
        'm': 'meters',
        'meter': 'meters',
        'km': 'kilometers',
        'kilometer': 'kilometers',
        'mi': 'miles',
        'mile': 'miles',
        'ft': 'feet',
        'foot': 'feet',
        'in': 'inches',
        'inch': 'inches',
        'cm': 'centimeters',
        'centimeter': 'centimeters',

        # Weight
        'kg': 'kilograms',
        'kilogram': 'kilograms',
        'g': 'grams',
        'gram': 'grams',
        'lb': 'pounds',
        'lbs': 'pounds',
        'pound': 'pounds',
        'oz': 'ounces',
        'ounce': 'ounces',

        # Volume
        'l': 'liters',
        'liter': 'liters',
        'ml': 'milliliters',
        'milliliter': 'milliliters',
        'gal': 'gallons',
        'gallon': 'gallons',
        'cup': 'cups',
    }

    # Resolve aliases
    from_unit = unit_aliases.get(from_unit, from_unit)
    to_unit = unit_aliases.get(to_unit, to_unit)

    # Unit categories and their base conversions
    unit_categories = {
        'temperature': {
            'celsius': lambda x: x,
            'fahrenheit': lambda x: (x - 32) * 5/9,
            'kelvin': lambda x: x - 273.15,
        },
        'length': {
            'meters': lambda x: x,
            'kilometers': lambda x: x * 1000,
            'miles': lambda x: x * 1609.344,
            'feet': lambda x: x * 0.3048,
            'inches': lambda x: x * 0.0254,
            'centimeters': lambda x: x * 0.01,
        },
        'weight': {
            'kilograms': lambda x: x,
            'grams': lambda x: x * 0.001,
            'pounds': lambda x: x * 0.453592,
            'ounces': lambda x: x * 0.0283495,
        },
        'volume': {
            'liters': lambda x: x,
            'milliliters': lambda x: x * 0.001,
            'gallons': lambda x: x * 3.78541,
            'cups': lambda x: x * 0.236588,
        },
    }

    # Inverse conversions (from base unit)
    inverse_conversions = {
        'temperature': {
            'celsius': lambda x: x,
            'fahrenheit': lambda x: x * 9/5 + 32,
            'kelvin': lambda x: x + 273.15,
        },
        'length': {
            'meters': lambda x: x,
            'kilometers': lambda x: x / 1000,
            'miles': lambda x: x / 1609.344,
            'feet': lambda x: x / 0.3048,
            'inches': lambda x: x / 0.0254,
            'centimeters': lambda x: x / 0.01,
        },
        'weight': {
            'kilograms': lambda x: x,
            'grams': lambda x: x / 0.001,
            'pounds': lambda x: x / 0.453592,
            'ounces': lambda x: x / 0.0283495,
        },
        'volume': {
            'liters': lambda x: x,
            'milliliters': lambda x: x / 0.001,
            'gallons': lambda x: x / 3.78541,
            'cups': lambda x: x / 0.236588,
        },
    }

    # Find which category each unit belongs to
    from_category = None
    to_category = None

    for category, units in unit_categories.items():
        if from_unit in units:
            from_category = category
        if to_unit in units:
            to_category = category

    # Validate units exist
    if from_category is None:
        all_units = []
        for units in unit_categories.values():
            all_units.extend(units.keys())
        raise ValueError(f"Unsupported unit '{from_unit}'. Supported units: {', '.join(sorted(all_units))}")

    if to_category is None:
        all_units = []
        for units in unit_categories.values():
            all_units.extend(units.keys())
        raise ValueError(f"Unsupported unit '{to_unit}'. Supported units: {', '.join(sorted(all_units))}")

    # Validate units are in the same category
    if from_category != to_category:
        raise ValueError(
            f"Cannot convert between different unit types: '{from_unit}' ({from_category}) "
            f"and '{to_unit}' ({to_category})"
        )

    # Perform conversion: source → base unit → target unit
    base_value = unit_categories[from_category][from_unit](value)
    result = inverse_conversions[to_category][to_unit](base_value)

    return result
