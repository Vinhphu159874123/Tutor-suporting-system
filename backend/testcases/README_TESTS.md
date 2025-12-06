# Tutor Support System - Test Suite

Comprehensive functional and non-functional test suite for the Tutor Support System.

## Test Coverage

### Functional Tests (F-01 to F-25)
- **Account Management**: Login, Profile, Session Validation, Logout
- **Registration**: Student/Tutor registration, Status viewing, Coordinator review
- **Scheduling**: Session creation, Availability setting, Organizing, Rescheduling
- **Session Management**: Conducting sessions, Attendance, Materials upload/download, Progress tracking, Feedback
- **Reporting**: Course reports, Statistics
- **Administration**: User account management
- **Forum**: Study group creation

### Non-Functional Tests (NF-01 to NF-10)
- **Performance**: Concurrent logins, Dashboard loading (30-50 sessions)
- **Security**: Unauthorized access prevention, Session access control
- **Scalability**: Large dataset handling, Concurrent updates
- **Load & Stability**: 50 concurrent users, Bulk registrations
- **Database Integrity**: Double-booking prevention, Historical data preservation

## Prerequisites

```bash
# Install required packages
pip install pytest httpx pytest-asyncio matplotlib numpy

# Optional: For JSON reports
pip install pytest-json-report
```

## Test Configuration

Edit test files to configure your test accounts:

```python
TEST_STUDENT = {"email": "your-student@hcmut.edu.vn", "password": "password"}
TEST_TUTOR = {"email": "your-tutor@hcmut.edu.vn", "password": "password"}
TEST_COORDINATOR = {"email": "your-coordinator@hcmut.edu.vn", "password": "password"}
```

## Running Tests

### Run All Tests
```bash
# Run complete test suite with report
python run_all_tests.py
```

### Run Individual Test Suites
```bash
# Functional tests part 1 (F-01 to F-10)
pytest test_functional_part1.py -v -s

# Functional tests part 2 (F-11 to F-20)
pytest test_functional_part2.py -v -s

# Functional tests part 3 (F-21 to F-25)
pytest test_functional_part3.py -v -s

# Non-functional tests (NF-01 to NF-10)
pytest test_nonfunctional.py -v -s
```

### Run Specific Test
```bash
# Run single test by name
pytest test_functional_part1.py::TestFunctionalPart1::test_f01_login_with_sso -v -s

# Run tests matching pattern
pytest -k "login" -v -s
```

## Performance Analysis

Generate performance metrics and visualization:

```bash
python generate_performance_charts.py
```

This will:
1. Measure response times for key endpoints
2. Calculate P50, P95, min/max metrics
3. Generate performance charts (PNG)
4. Create JSON report with detailed metrics

Output files:
- `performance_report_YYYYMMDD_HHMMSS.json` - Detailed metrics
- `performance_chart_YYYYMMDD_HHMMSS.png` - Visualization charts

## Test Reports

### Console Output
- ✅ PASSED - Test passed all assertions
- ❌ FAILED - Test failed with error
- ⚠️ SKIPPED - Test skipped (missing test data or preconditions)

### JSON Reports
Enable JSON reporting:
```bash
pytest --json-report --json-report-file=report.json
```

## Expected Results

Based on the requirements document:

### Functional Tests
- All 25 functional test cases should **PASS**
- Some tests may be SKIPPED if test data is not available
- Tests validate: Authentication, CRUD operations, Business logic, Access control

### Non-Functional Tests
- **NF-01**: 95% of concurrent logins complete within 3s
- **NF-02**: Dashboard loads within 4-5s with 30-50 sessions
- **NF-03/NF-04**: Unauthorized access returns 403/404
- **NF-05**: Large dataset operations within 3-4s
- **NF-06**: Concurrent updates maintain consistency
- **NF-07**: System stable under sustained load
- **NF-08**: Bulk registrations < 5s response time
- **NF-09**: Double-booking prevented by system
- **NF-10**: Historical data preserved (soft-delete)

## Performance Benchmarks

Target metrics from requirements:

| Metric | Target | Test |
|--------|--------|------|
| Concurrent Users | 30-40 | NF-01 |
| Dashboard Load | < 5s | NF-02 |
| API Response (P95) | < 3s | Performance Analysis |
| Error Rate | < 5% | All Tests |
| Success Rate | > 95% | Load Tests |

## Troubleshooting

### Tests Fail with 401 Unauthorized
- Check test credentials in test files
- Verify accounts exist and have correct roles
- Check token expiration settings

### Tests Timeout
- Increase timeout in AsyncClient
- Check network connectivity to production server
- Railway/Vercel may have cold start delays

### Performance Tests Show High Response Times
- Railway free tier may have resource limits
- Redis might not be available (check warnings)
- Database connection pooling issues

### Missing Test Data
- Some tests require existing sessions/materials
- Create test data via UI or populate script
- Tests will SKIP if data not found

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: cd backend/testcases && python run_all_tests.py
```

## Test Maintenance

- Update test credentials when accounts change
- Add new tests for new features
- Keep test data synchronized with production schema
- Review and update performance benchmarks quarterly

## Contributing

When adding new tests:
1. Follow existing naming convention (test_fXX_ or test_nfXX_)
2. Add clear docstrings explaining scenario and expected result
3. Handle missing data gracefully (SKIP instead of FAIL)
4. Update this README with new test descriptions

## Contact

For questions or issues with tests:
- Check logs in test output
- Review Railway/Vercel deployment logs
- Verify Supabase connection and RLS policies
