"""
Script to fix all login calls in test files to use form data instead of JSON
"""
import re

files_to_fix = [
    "test_functional_part1.py",
    "test_functional_part2.py",
    "test_functional_part3.py",
    "test_nonfunctional.py"
]

def fix_login_calls(filepath):
    print(f"\nFixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern 1: await client.post("/auth/login", json=TEST_STUDENT)
    # Replace with: await client.post("/auth/login", data={"username": TEST_STUDENT["email"], "password": TEST_STUDENT["password"]}, headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    # Update test credentials first
    old_credentials = [
        ('TEST_STUDENT = {\n    "email": "student.test@hcmut.edu.vn",\n    "password": "test123456"\n}',
         'TEST_STUDENT = {\n    "email": "student113@hcmut.edu.vn",\n    "password": "TestPass123!"\n}'),
        ('TEST_TUTOR = {\n    "email": "tutor.test@hcmut.edu.vn", \n    "password": "test123456"\n}',
         'TEST_TUTOR = {\n    "email": "tutor113@hcmut.edu.vn", \n    "password": "TestPass123!"\n}'),
        ('TEST_COORDINATOR = {\n    "email": "coordinator.test@hcmut.edu.vn",\n    "password": "test123456"\n}',
         'TEST_COORDINATOR = {\n    "email": "coordinator113@hcmut.edu.vn",\n    "password": "TestPass123!"\n}'),
        ('TEST_ADMIN = {\n    "email": "admin.test@hcmut.edu.vn",\n    "password": "admin123"\n}',
         'TEST_ADMIN = {\n    "email": "admin113@hcmut.edu.vn",\n    "password": "TestPass123!"\n}'),
    ]
    
    for old, new in old_credentials:
        content = content.replace(old, new)
    
    # Fix simple login calls: json=TEST_STUDENT -> data=TEST_STUDENT with headers
    patterns = [
        (r'await client\.post\("/auth/login", json=(TEST_\w+)\)',
         r'await client.post("/auth/login", data={"username": \1["email"], "password": \1["password"]}, headers={"Content-Type": "application/x-www-form-urlencoded"})'),
        (r'await client\.post\(\s*"/auth/login",\s*json=(TEST_\w+)\s*\)',
         r'await client.post("/auth/login", data={"username": \1["email"], "password": \1["password"]}, headers={"Content-Type": "application/x-www-form-urlencoded"})'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {filepath}")

if __name__ == "__main__":
    for file in files_to_fix:
        try:
            fix_login_calls(file)
        except FileNotFoundError:
            print(f"⚠️  File not found: {file}")
        except Exception as e:
            print(f"❌ Error fixing {file}: {e}")
    
    print("\n✅ All files fixed!")
