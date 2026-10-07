#!/usr/bin/env python3
"""Production entry point for validated PlayerCharacters_v22 canonical articulated arms."""
from pathlib import Path
import runpy, sys

here=Path(__file__).resolve().parent
if len(sys.argv)<2:
    sys.argv=[sys.argv[0],"game"]

runpy.run_path(str(here/"apply_pc22_canonical_arm_candidate.py"),run_name="__main__")
runpy.run_path(str(here/"finalize_pc22_canonical_arms_production.py"),run_name="__main__")
