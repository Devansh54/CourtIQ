"""CourtIQ — Streamlit Community Cloud Entry Point.

Delegates execution directly to app.py to satisfy default Streamlit Cloud path expectations.
"""

import runpy
import sys
from pathlib import Path

# Ensure root and src are on sys.path
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

runpy.run_path(str(_ROOT / "app.py"), run_name="__main__")
