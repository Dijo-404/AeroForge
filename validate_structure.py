#!/usr/bin/env python3
"""Validation script for AeroForge project structure."""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report."""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description} MISSING: {filepath}")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists and report."""
    if Path(dirpath).is_dir():
        print(f"✓ {description}: {dirpath}")
        return True
    else:
        print(f"✗ {description} MISSING: {dirpath}")
        return False

def main():
    print("=" * 60)
    print("AeroForge Project Structure Validation")
    print("=" * 60)
    
    all_checks = []
    
    # Check core configuration files
    print("\n📋 Configuration Files:")
    all_checks.append(check_file_exists("pyproject.toml", "pyproject.toml"))
    all_checks.append(check_file_exists("requirements.txt", "requirements.txt"))
    all_checks.append(check_file_exists(".env.template", ".env.template"))
    all_checks.append(check_file_exists(".env", ".env (actual config)"))
    
    # Check directory structure
    print("\n📁 Directory Structure:")
    all_checks.append(check_directory_exists("src", "src/"))
    all_checks.append(check_directory_exists("src/agents", "src/agents/"))
    all_checks.append(check_directory_exists("src/tools", "src/tools/"))
    all_checks.append(check_directory_exists("src/synthesis", "src/synthesis/"))
    all_checks.append(check_directory_exists("tests", "tests/"))
    
    # Check __init__.py files
    print("\n🐍 Python Package Files:")
    all_checks.append(check_file_exists("src/__init__.py", "src/__init__.py"))
    all_checks.append(check_file_exists("src/agents/__init__.py", "src/agents/__init__.py"))
    all_checks.append(check_file_exists("src/tools/__init__.py", "src/tools/__init__.py"))
    all_checks.append(check_file_exists("src/synthesis/__init__.py", "src/synthesis/__init__.py"))
    all_checks.append(check_file_exists("tests/__init__.py", "tests/__init__.py"))
    
    # Check core module files
    print("\n📦 Core Modules:")
    all_checks.append(check_file_exists("src/config.py", "src/config.py"))
    all_checks.append(check_file_exists("src/main_workflow.py", "src/main_workflow.py"))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    print(f"Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✅ All structure checks passed!")
        return 0
    else:
        print("❌ Some checks failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
