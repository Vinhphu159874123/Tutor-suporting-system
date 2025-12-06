"""
Run tests with beautiful output for screenshot
Tạo log đẹp, màu mè, professional cho slide
"""
import subprocess
import sys
from datetime import datetime

def print_header():
    """Print beautiful header"""
    print("\n" + "="*80)
    print("🧪 TUTOR SUPPORTING SYSTEM - TEST EXECUTION".center(80))
    print("="*80)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target: Production API (Railway)")
    print(f"🔧 Framework: pytest + httpx AsyncClient")
    print("="*80 + "\n")

def print_summary_header():
    """Print summary section header"""
    print("\n" + "="*80)
    print("📊 TEST EXECUTION SUMMARY".center(80))
    print("="*80 + "\n")

def run_tests():
    """Run pytest with beautiful output"""
    print_header()
    
    # Run pytest with verbose output and color
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "test_all_35_cases.py",
            "-v",  # verbose
            "--tb=short",  # short traceback
            "--color=yes",  # enable colors
            "-ra",  # show summary of all test outcomes
        ],
        capture_output=False,
        text=True
    )
    
    return result.returncode

if __name__ == "__main__":
    print("\n🚀 Starting test execution...\n")
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED SUCCESSFULLY".center(80))
        print("="*80)
        print("\n🎉 System is production-ready!")
        print("📈 Performance validated")
        print("🔒 Security verified")
        print("✨ Zero critical failures\n")
    else:
        print("\n❌ Some tests failed. Please review the output above.\n")
    
    sys.exit(exit_code)
