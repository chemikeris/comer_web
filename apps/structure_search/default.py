import copy

settings = {
    's': 0.5,
    'sort': 2,
    'nhits': 1000,
    'presimilarity': 0.0,
    'prescore': 0.4,
    'speed': 13,
    }

complex_settings = copy.deepcopy(settings)
complex_settings.update(
    {
        'speed': 16,
        'sort': 0,
    }
)
