#!/usr/bin/env python3
"""Prepend a robust sys.path guard cell so the notebook runs from any cwd."""
import json
from pathlib import Path

nb_path = Path("notebooks/01_analysis_walkthrough.ipynb")
nb = json.loads(nb_path.read_text())

guard = (
    "# --- environment guard: make src/ importable from any working directory ---\n"
    "import os, sys\n"
    "ROOT = Path(os.getcwd()).resolve()\n"
    "if ROOT.name == 'notebooks':\n"
    "    ROOT = ROOT.parent\n"
    "if str(ROOT) not in sys.path:\n"
    "    sys.path.insert(0, str(ROOT))\n"
    "os.chdir(ROOT)\n"
)
# Use Path imported inside the cell (cell below imports it too, but be safe)
guard = guard.replace("from pathlib import Path\n", "", 1)
guard_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import os, sys\n",
        "from pathlib import Path\n",
        "ROOT = Path(os.getcwd()).resolve()\n",
        "if ROOT.name == \"notebooks\":\n",
        "    ROOT = ROOT.parent\n",
        "if str(ROOT) not in sys.path:\n",
        "    sys.path.insert(0, str(ROOT))\n",
        "os.chdir(ROOT)\n",
        "print(\"working dir:\", ROOT)\n",
    ],
}

# insert as first cell
nb["cells"].insert(0, guard_cell)
# clear execution counts/outputs so the next execute run is authoritative
for c in nb["cells"]:
    if c["cell_type"] == "code":
        c["execution_count"] = None
        c["outputs"] = []
nb_path.write_text(json.dumps(nb, indent=1) + "\n")
print(f"inserted guard cell; total cells now {len(nb['cells'])}")
