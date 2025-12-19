#!/usr/bin/env python3
"""
Auto-export script for presentation and handout PDFs
Cross-platform solution using typst-py package
"""

import typst
import os
import sys
from pathlib import Path


def compile_dual_pdfs(input_file):
    """Compile both presentation and handout PDFs from a Typst file"""

    # Get the base name without extension
    input_path = Path(input_file)
    base_name = input_path.stem

    print(f"Compiling presentation PDF...")
    # Compile normal presentation
    typst.compile(input_file, output=f"{base_name}.pdf")

    print(f"Compiling handout PDF...")
    # Compile handout version with handout mode enabled
    typst.compile(
        input_file, output=f"{base_name}_handout.pdf", sys_inputs={"handout": "true"}
    )

    print("Done! Generated:")
    print(f"  - {base_name}.pdf (presentation)")
    print(f"  - {base_name}_handout.pdf (handout)")


if __name__ == "__main__":
    # Use command line argument or default to presentation.typ
    input_file = sys.argv[1] if len(sys.argv) > 1 else "presentation.typ"

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found!")
        sys.exit(1)

    compile_dual_pdfs(input_file)
