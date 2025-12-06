"""
Test Runner - Run all functional and non-functional tests
Generates comprehensive test report with results
"""
import subprocess
import sys
import json
from datetime import datetime
import os

def run_tests():
    """Run all test suites and collect results"""
    
    print("=" * 80)
    print("TUTOR SUPPORT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_files = [
        ("Functional Tests Part 1 (F-01 to F-10)", "test_functional_part1.py"),
        ("Functional Tests Part 2 (F-11 to F-20)", "test_functional_part2.py"),
        ("Functional Tests Part 3 (F-21 to F-25)", "test_functional_part3.py"),
        ("Non-Functional Tests (NF-01 to NF-10)", "test_nonfunctional.py"),
    ]
    
    results = []
    
    for suite_name, test_file in test_files:
        print("-" * 80)
        print(f"Running: {suite_name}")
        print("-" * 80)
        
        try:
            # Run pytest with JSON report
            result = subprocess.run(
                [
                    sys.executable, "-m", "pytest",
                    test_file,
                    "-v",
                    "-s",
                    "--tb=short",
                    "--json-report",
                    f"--json-report-file=results_{test_file.replace('.py', '.json')}"
                ],
                cwd=os.path.dirname(__file__),
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes per suite
            )
            
            # Parse output
            output = result.stdout + result.stderr
            
            results.append({
                "suite": suite_name,
                "file": test_file,
                "returncode": result.returncode,
                "output": output,
                "success": result.returncode == 0
            })
            
            print(output)
            
        except subprocess.TimeoutExpired:
            print(f"⚠️  TIMEOUT: {suite_name} exceeded time limit")
            results.append({
                "suite": suite_name,
                "file": test_file,
                "returncode": -1,
                "output": "Test suite timed out",
                "success": False
            })
        except Exception as e:
            print(f"❌ ERROR: {suite_name} failed with exception: {e}")
            results.append({
                "suite": suite_name,
                "file": test_file,
                "returncode": -1,
                "output": str(e),
                "success": False
            })
    
    # Generate summary report
    print("\n")
    print("=" * 80)
    print("TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    total_suites = len(results)
    passed_suites = sum(1 for r in results if r["success"])
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status}: {result['suite']}")
    
    print()
    print(f"Overall: {passed_suites}/{total_suites} test suites passed")
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Save full report
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_suites": total_suites,
                "passed_suites": passed_suites,
                "failed_suites": total_suites - passed_suites
            },
            "results": results
        }, f, indent=2)
    
    print(f"\nFull report saved to: {report_file}")
    
    return passed_suites == total_suites


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
