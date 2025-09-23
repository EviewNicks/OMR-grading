#!/usr/bin/env python3
"""
Environment Validation Script for OMR Grading System
====================================================

Comprehensive validation script that checks:
1. UV package installer installation dan functionality
2. Python version compatibility (3.9+)
3. Core dependencies (OpenCV, NumPy, Matplotlib, Pandas)
4. Basic OpenCV operations functionality
5. Virtual environment status

Author: OMR Development Team
Date: Week 1 - Day 1 Implementation
"""

import sys
import subprocess
import importlib.util
from pathlib import Path


def validate_uv_installation():
    """
    Validasi instalasi UV package installer

    Returns:
        bool: True jika UV terinstall dan functional
    """
    print("Checking UV installation...")
    try:
        result = subprocess.run(['uv', '--version'],
                              capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print(f"UV: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("UV tidak terinstall atau tidak ditemukan")
        print(" Install UV dengan: winget install --id=astral-sh.uv -e")
        return False


def validate_python_version():
    """
    Validasi versi Python (minimal 3.9+)

    Returns:
        bool: True jika Python version memenuhi requirement
    """
    print("Checking Python version...")
    python_version = sys.version_info

    if python_version >= (3, 9):
        print(f" Python: {sys.version}")
        return True
    else:
        print(f" Python {python_version.major}.{python_version.minor} detected")
        print(" OMR System membutuhkan Python 3.9 atau lebih tinggi")
        return False


def validate_virtual_environment():
    """
    Validasi apakah script berjalan dalam virtual environment

    Returns:
        bool: True jika dalam virtual environment
    """
    print(" Checking virtual environment...")

    # Check jika dalam virtual environment
    in_venv = (hasattr(sys, 'real_prefix') or
               (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

    if in_venv:
        venv_path = Path(sys.prefix).name
        print(f" Virtual Environment: {venv_path}")
        return True
    else:
        print(" Tidak dalam virtual environment")
        print("Aktivasi environment: .\\omr_env\\Scripts\\activate")
        return False


def validate_package_installation(package_name, import_name=None, required_version=None):
    """
    Validasi instalasi package tertentu

    Args:
        package_name (str): Nama package untuk display
        import_name (str): Nama untuk import (default: package_name)
        required_version (str): Versi minimum yang dibutuhkan

    Returns:
        tuple: (bool, str) - (status, version_info)
    """
    if import_name is None:
        import_name = package_name.lower().replace('-', '_')

    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'Unknown')

        print(f" {package_name}: {version}")

        # Version check jika diperlukan
        if required_version and hasattr(module, '__version__'):
            # Basic version comparison (simplified)
            if version >= required_version:
                return True, version
            else:
                print(f"  Version {version} mungkin tidak compatible (required: {required_version})")
                return True, version  # Still functional, just warning

        return True, version

    except ImportError:
        print(f" {package_name}: Not installed")
        return False, None


def test_opencv_functionality():
    """
    Test basic OpenCV operations untuk memastikan fungsionalitas

    Returns:
        bool: True jika OpenCV berfungsi dengan baik
    """
    print(" Testing OpenCV functionality...")

    try:
        import cv2
        import numpy as np

        # Test 1: Create test image
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        if test_img.shape != (100, 100, 3):
            raise ValueError("NumPy array creation failed")

        # Test 2: Basic OpenCV operations
        gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Test 3: Image processing operations
        _, thresh = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

        print(" OpenCV basic operations: Working!")
        print("  - Image creation: ok")
        print("  - Color conversion: ok")
        print("  - Gaussian blur: ok")
        print("  - Thresholding: ok")

        return True

    except Exception as e:
        print(f" OpenCV functionality test failed: {e}")
        return False


def test_matplotlib_functionality():
    """
    Test basic Matplotlib functionality

    Returns:
        bool: True jika Matplotlib berfungsi dengan baik
    """
    print(" Testing Matplotlib functionality...")

    try:
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        import numpy as np

        # Simple plot test
        x = np.linspace(0, 10, 100)
        y = np.sin(x)

        fig, ax = plt.subplots()
        ax.plot(x, y)
        plt.close(fig)  # Clean up

        print(" Matplotlib functionality: Working!")
        return True

    except Exception as e:
        print(f" Matplotlib functionality test failed: {e}")
        return False


def main():
    """
    Main validation function yang menjalankan semua checks
    """
    print("=" * 60)
    print(" ENVIRONMENT VALIDATION UNTUK OMR GRADING SYSTEM")
    print("=" * 60)

    validation_results = {}

    # Core System Validation
    print("\n CORE SYSTEM VALIDATION")
    print("-" * 30)
    validation_results['python'] = validate_python_version()
    validation_results['uv'] = validate_uv_installation()
    validation_results['venv'] = validate_virtual_environment()

    # Package Installation Validation
    print("\n PACKAGE INSTALLATION VALIDATION")
    print("-" * 35)

    packages_to_check = [
        ('OpenCV', 'cv2'),
        ('NumPy', 'numpy'),
        ('Matplotlib', 'matplotlib'),
        ('Pandas', 'pandas')
    ]

    for package_name, import_name in packages_to_check:
        success, version = validate_package_installation(package_name, import_name)
        validation_results[import_name] = success

    # Functionality Testing
    print("\n FUNCTIONALITY TESTING")
    print("-" * 25)
    validation_results['opencv_func'] = test_opencv_functionality()
    validation_results['matplotlib_func'] = test_matplotlib_functionality()

    # Results Summary
    print("\n" + "=" * 60)
    print(" VALIDATION SUMMARY")
    print("=" * 60)

    total_checks = len(validation_results)
    passed_checks = sum(validation_results.values())
    success_rate = (passed_checks / total_checks) * 100

    print(f"Total Checks: {total_checks}")
    print(f"Passed: {passed_checks}")
    print(f"Failed: {total_checks - passed_checks}")
    print(f"Success Rate: {success_rate:.1f}%")

    if success_rate == 100:
        print("\n ENVIRONMENT VALIDATION SUCCESSFUL!")
        print(" Semua sistem siap untuk OMR development")
        print(" Lanjut ke tahap Dataset Organization (Day 2)")
        return 0
    elif success_rate >= 80:
        print("\n  ENVIRONMENT MOSTLY READY")
        print(" Beberapa komponen memerlukan attention")
        print(" Review failed checks dan perbaiki sebelum lanjut")
        return 1
    else:
        print("\n ENVIRONMENT VALIDATION FAILED")
        print(" Perbaiki masalah di atas sebelum melanjutkan")
        print(" Refer to setup documentation untuk troubleshooting")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)