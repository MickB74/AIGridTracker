import os
import pathlib
import json

def load_local_secrets() -> dict:
    """Best-effort local API keys for dev convenience, so keys needn't be pasted
    each session. Never raises; returns {'eia': str, 'pjm': str} (blank if absent).
    Lookup order per key: environment variable -> ./.env -> sibling
    pjm-suite/PJM_Data_Hub/config.json. Nothing is committed — .gitignore blocks
    .env and config.json. The UI fields still override whatever is found here."""
    out = {"eia": os.environ.get("EIA_API_KEY", "").strip(),
           "pjm": os.environ.get("PJM_API_KEY", "").strip()}
    
    # Resolve project root relative to this file: src/services/secrets.py -> root/
    here = pathlib.Path(__file__).resolve().parent.parent.parent

    env_path = here / ".env"
    if env_path.exists():
        try:
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                if k.strip() == "EIA_API_KEY" and not out["eia"]:
                    out["eia"] = v
                elif k.strip() == "PJM_API_KEY" and not out["pjm"]:
                    out["pjm"] = v
        except Exception:                                          # noqa: BLE001
            pass

    if not out["eia"] or not out["pjm"]:
        cfg = here.parent / "pjm-suite" / "PJM_Data_Hub" / "config.json"
        try:
            data = json.loads(cfg.read_text())
            out["eia"] = out["eia"] or str(data.get("eia_api_key", "")).strip()
            out["pjm"] = out["pjm"] or str(data.get("subscription_key", "")).strip()
        except Exception:                                          # noqa: BLE001
            pass
    return out
