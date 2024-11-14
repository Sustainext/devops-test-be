def convert_to_gj(quantity, unit):
    conversion_factors = {
        "Joules": 1e-9,
        "KJ": 1e-6,
        "Wh": 0.0000036,
        "KWh": 0.0036,
        "GJ": 1,
        "MMBtu": 1.05506,
    }

    factor = conversion_factors.get(unit)
    # * Converting to GJ
    return round(factor * quantity, 5)
