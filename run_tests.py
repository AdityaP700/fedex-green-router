#!/usr/bin/env python3
import argparse
import subprocess
import sys
from typing import List

def run_tests(args: argparse.Namespace) -> int:
    """Run the tests with the specified configuration."""
    cmd: List[str] = ["pytest"]
    
    # Add markers based on test type
    if args.unit:
        cmd.append("-m unit")
    if args.integration:
        cmd.append("-m integration")
    if args.api:
        cmd.append("-m api")
    if args.ml:
        cmd.append("-m ml")
    
    # Add coverage options
    if args.coverage:
        cmd.extend([
            "--cov=fedex-green-router",
            "--cov-report=term-missing",
            "--cov-report=html",
            "--cov-branch"
        ])
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add fail fast option
    if args.fail_fast:
        cmd.append("-x")
    
    # Add test file pattern
    if args.pattern:
        cmd.append(args.pattern)
    
    # Run tests in parallel if requested
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add any additional pytest arguments
    if args.pytest_args:
        cmd.extend(args.pytest_args)
    
    # Run the tests
    try:
        result = subprocess.run(" ".join(cmd), shell=True, check=False)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}", file=sys.stderr)
        return 1

def main() -> int:
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(description="Run the test suite for FedEx Green Router")
    
    # Test type arguments
    test_type = parser.add_argument_group("Test Type")
    test_type.add_argument("--unit", action="store_true", help="Run unit tests")
    test_type.add_argument("--integration", action="store_true", help="Run integration tests")
    test_type.add_argument("--api", action="store_true", help="Run API tests")
    test_type.add_argument("--ml", action="store_true", help="Run machine learning tests")
    test_type.add_argument("--all", action="store_true", help="Run all tests")
    
    # Coverage arguments
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    
    # Test running arguments
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-x", "--fail-fast", action="store_true", help="Stop on first failure")
    parser.add_argument("-p", "--pattern", help="Test file pattern to match")
    parser.add_argument("-n", "--parallel", type=int, help="Number of parallel processes")
    
    # Additional pytest arguments
    parser.add_argument("pytest_args", nargs="*", help="Additional pytest arguments")
    
    args = parser.parse_args()
    
    # If no test type is specified, run all tests
    if not any([args.unit, args.integration, args.api, args.ml]):
        args.all = True
    
    return run_tests(args)

if __name__ == "__main__":
    sys.exit(main()) 