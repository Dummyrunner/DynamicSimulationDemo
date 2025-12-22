#!/usr/bin/env python3
"""
Auto-export script for presentation and handout PDFs
Uses wrapper files to control handout mode in Typst
"""

import os
import subprocess
import sys
from pathlib import Path


def compile_dual_pdfs(input_file):
    """Compile both presentation and handout PDFs from a Typst file"""

    input_path = Path(input_file)
    base_name = input_path.stem
    input_dir = input_path.parent

    # Read the original presentation file
    with open(input_path, "r", encoding="utf-8") as f:
        presentation_content = f.read()

    print("Compiling presentation PDF...")
    # Create wrapper for presentation mode (handout = false)
    wrapper_pres_content = f"""#let handout = false
{presentation_content}
"""
    wrapper_pres_file = input_dir / f"{base_name}_pres_wrapper.typ"
    wrapper_pres_file.write_text(wrapper_pres_content, encoding="utf-8")

    result_pres = subprocess.run(
        ["typst", "compile", str(wrapper_pres_file), f"{base_name}.pdf"],
        cwd=input_dir,
        capture_output=False,
        text=True,
    )

    # Clean up wrapper file
    wrapper_pres_file.unlink()

    if result_pres.returncode != 0:
        print("Error compiling presentation!")
        sys.exit(1)

    print("Compiling handout PDF...")
    # Create wrapper for handout mode (handout = true)
    wrapper_handout_content = f"""#let handout = true
{presentation_content}
"""
    wrapper_handout_file = input_dir / f"{base_name}_handout_wrapper.typ"
    wrapper_handout_file.write_text(wrapper_handout_content, encoding="utf-8")

    result_handout = subprocess.run(
        ["typst", "compile", str(wrapper_handout_file), f"{base_name}_handout.pdf"],
        cwd=input_dir,
        capture_output=False,
        text=True,
    )

    # Clean up wrapper file
    wrapper_handout_file.unlink()

    if result_handout.returncode != 0:
        print("Error compiling handout!")
        sys.exit(1)

    print("Done! Generated:")
    print(f"  - {base_name}.pdf (presentation with animations)")
    print(f"  - {base_name}_handout.pdf (handout without animations)")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "presentation.typ"

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found!")
        sys.exit(1)

    compile_dual_pdfs(input_file)
