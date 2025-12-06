"""
Script to fix all test methods to create their own AsyncClient instead of using fixtures
"""
import re

def fix_test_file(filepath):
    print(f"\nFixing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove fixture definitions
    content = re.sub(
        r'    @pytest\.fixture\s+async def client\(self\):.*?yield client\s+',
        '',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'    @pytest\.fixture\s+async def \w+_token\(self.*?\):.*?return .*?\n\n',
        '',
        content,
        flags=re.DOTALL
    )
    
    # Fix test methods: Remove fixtures from parameter list and add client creation
    # Pattern: async def test_xxx(self, client, ...): -> async def test_xxx(self):
    
    # First, find all test methods with fixtures
    test_pattern = r'(    @pytest\.mark\.asyncio\s+async def (test_\w+)\(self)(, [^)]+)(\):)'
    
    def replace_test(match):
        prefix = match.group(1)  # "    @pytest.mark.asyncio\n    async def test_xxx(self"
        test_name = match.group(2)  # "test_xxx"
        params = match.group(3)  # ", client, student_token"
        suffix = match.group(4)  # "):"
        
        # Remove all fixture parameters
        return f'{prefix}):'
    
    content = re.sub(test_pattern, replace_test, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed {filepath}")

if __name__ == "__main__":
    files = [
        "test_functional_part1.py",
        "test_functional_part2.py",
        "test_functional_part3.py",
        "test_nonfunctional.py"
    ]
    
    for file in files:
        try:
            fix_test_file(file)
        except Exception as e:
            print(f"❌ Error fixing {file}: {e}")
    
    print("\n✅ All files fixed - removed fixture parameters!")
    print("⚠️  NOTE: You'll need to manually add `async with AsyncClient(...) as client:` in each test")
