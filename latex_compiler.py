#!/usr/bin/env python3
"""
LaTeX Compiler Module for Web2PDF Agent
Provides functionality to compile LaTeX documents with XeLaTeX engine
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple


class Colors:
    """ANSI color codes for terminal output"""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    BOLD = "\033[1m"
    NC = "\033[0m"  # No Color


class LaTeXCompiler:
    """Enhanced LaTeX compiler with better error handling and output"""

    def __init__(self, verbose: bool = True):
        """Initialize the LaTeX compiler

        Args:
            verbose: Enable detailed output during compilation
        """
        self.verbose = verbose

    def print_colored(self, message: str, color: str = Colors.NC) -> None:
        """Print colored message to terminal"""
        if self.verbose:
            print(f"{color}{message}{Colors.NC}")

    def check_xelatex(self) -> bool:
        """Check if XeLaTeX is available"""
        try:
            subprocess.run(["xelatex", "--version"], capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def run_xelatex(self, tex_file: Path, output_dir: Path) -> Tuple[bool, str]:
        """Run XeLaTeX compilation"""
        if not self.check_xelatex():
            return False, "XeLaTeX not found. Please install TeXLive or MiKTeX."

        # Change to output directory for compilation
        original_cwd = os.getcwd()

        try:
            os.chdir(output_dir)

            cmd = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", str(tex_file.resolve())]

            self.print_colored(f"🔄 Running: {' '.join(cmd)}", Colors.BLUE)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)  # 2 minute timeout

            if result.returncode == 0:
                self.print_colored("✅ XeLaTeX compilation successful", Colors.GREEN)
                return True, result.stdout
            else:
                self.print_colored("❌ XeLaTeX compilation failed", Colors.RED)
                error_msg = f"Exit code: {result.returncode}\n"
                error_msg += f"STDOUT:\n{result.stdout}\n"
                error_msg += f"STDERR:\n{result.stderr}"
                return False, error_msg

        except subprocess.TimeoutExpired:
            error_msg = "Compilation timed out after 2 minutes"
            self.print_colored(f"⏰ {error_msg}", Colors.YELLOW)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.print_colored(f"❌ {error_msg}", Colors.RED)
            return False, error_msg
        finally:
            os.chdir(original_cwd)

    def cleanup_aux_files(self, tex_file: Path, keep_pdf: bool = True) -> None:
        """Clean up auxiliary LaTeX files"""
        base_name = tex_file.stem
        aux_extensions = [".aux", ".log", ".out", ".toc", ".nav", ".snm", ".fls", ".fdb_latexmk"]

        if not keep_pdf:
            aux_extensions.append(".pdf")

        for ext in aux_extensions:
            aux_file = tex_file.parent / f"{base_name}{ext}"
            if aux_file.exists():
                try:
                    aux_file.unlink()
                    self.print_colored(f"🗑️  Removed: {aux_file.name}", Colors.YELLOW)
                except Exception as e:
                    self.print_colored(f"⚠️  Could not remove {aux_file.name}: {e}", Colors.YELLOW)

    def get_file_size(self, file_path: Path) -> str:
        """Get human-readable file size"""
        if not file_path.exists():
            return "0 B"

        size = file_path.stat().st_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def compile_document(self, tex_file_path: str, cleanup: bool = True, two_pass: bool = True) -> bool:
        """Compile a LaTeX document to PDF"""
        tex_file = Path(tex_file_path)

        if not tex_file.exists():
            self.print_colored(f"❌ File not found: {tex_file}", Colors.RED)
            return False

        if not tex_file.suffix.lower() == ".tex":
            self.print_colored(f"❌ File must have .tex extension: {tex_file}", Colors.RED)
            return False

        output_dir = tex_file.parent
        pdf_file = output_dir / f"{tex_file.stem}.pdf"

        self.print_colored(f"📝 Compiling: {tex_file.name}", Colors.BOLD)
        self.print_colored(f"📁 Output directory: {output_dir}", Colors.BLUE)

        # First pass
        success, output = self.run_xelatex(tex_file, output_dir)

        if not success:
            self.print_colored("❌ First pass failed", Colors.RED)
            if self.verbose:
                print(output)
            return False

        # Second pass for references/TOC (if requested)
        if two_pass:
            self.print_colored("🔄 Running second pass for references...", Colors.BLUE)
            success, output = self.run_xelatex(tex_file, output_dir)

            if not success:
                self.print_colored("❌ Second pass failed", Colors.RED)
                if self.verbose:
                    print(output)
                return False

        # Check if PDF was created
        if pdf_file.exists():
            file_size = self.get_file_size(pdf_file)
            self.print_colored(f"✅ PDF created: {pdf_file.name} ({file_size})", Colors.GREEN)
        else:
            self.print_colored("❌ PDF was not created", Colors.RED)
            return False

        # Cleanup auxiliary files
        if cleanup:
            self.print_colored("🧹 Cleaning up auxiliary files...", Colors.BLUE)
            self.cleanup_aux_files(tex_file, keep_pdf=True)

        return True


def main():
    """Command line interface for the LaTeX compiler"""
    if len(sys.argv) < 2:
        print("Usage: python latex_compiler.py <tex_file> [--no-cleanup] [--single-pass] [--quiet]")
        sys.exit(1)

    tex_file = sys.argv[1]
    cleanup = "--no-cleanup" not in sys.argv
    two_pass = "--single-pass" not in sys.argv
    verbose = "--quiet" not in sys.argv

    compiler = LaTeXCompiler(verbose=verbose)
    success = compiler.compile_document(tex_file, cleanup=cleanup, two_pass=two_pass)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
