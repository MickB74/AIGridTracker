from src.constants import SOURCES

def human_energy(wh: float) -> str:
    """Format energy (Wh) into equivalent hours/minutes of TV watching."""
    tv_seconds = wh / 0.24 * 9
    if tv_seconds < 60:
        return f"≈ {tv_seconds:.0f} seconds of watching TV"
    if tv_seconds < 3600:
        return f"≈ {tv_seconds/60:.1f} minutes of watching TV"
    return f"≈ {tv_seconds/3600:.1f} hours of watching TV"


def human_water(ml: float) -> str:
    """Format water volume (mL) into drops or liters."""
    drops = ml / 0.05
    return f"≈ {drops:.0f} drops of water" if drops < 100 else f"≈ {ml/1000:.2f} L of water"


def src_link(key: str) -> str:
    """Generate a markdown link to a primary source from constants.py."""
    if key not in SOURCES:
        return f"[{key}](https://www.google.com/)"
    name, url = SOURCES[key]
    return f"[{name}]({url})"
