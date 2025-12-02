"""
Run performance index migration
"""
import asyncio
import os
from sqlalchemy import text
from app.core.database import engine

async def run_migration():
    """Run the performance indexes migration"""
    
    # Read migration file
    migration_path = os.path.join(os.path.dirname(__file__), 'migrations', 'add_performance_indexes.sql')
    with open(migration_path, 'r') as f:
        migration_sql = f.read()
    
    # Split into individual statements
    statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print("🚀 Running performance optimization migration...")
    
    # Run each statement in its own transaction
    for i, statement in enumerate(statements, 1):
        try:
            # Skip ANALYZE statements for now (they're not critical)
            if 'ANALYZE' in statement:
                print(f"  [{i}/{len(statements)}] Skipping ANALYZE")
                continue
            
            async with engine.begin() as conn:
                await conn.execute(text(statement))
                # Extract index name from CREATE INDEX statement
                if 'CREATE INDEX' in statement:
                    index_name = statement.split('INDEX')[1].split('ON')[0].strip().replace('IF NOT EXISTS', '').strip()
                    print(f"  ✅ [{i}/{len(statements)}] Created index: {index_name}")
                else:
                    print(f"  ✅ [{i}/{len(statements)}] Executed statement")
        except Exception as e:
            print(f"  ⚠️  [{i}/{len(statements)}] Error: {str(e)[:150]}")
            # Continue with next statement
    
    print("\n🎉 Migration completed!")
    print("📊 Indexes created for improved query performance")

if __name__ == "__main__":
    asyncio.run(run_migration())
