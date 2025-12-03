"""
Fix file paths in database - convert Windows backslashes to Unix forward slashes
"""
import asyncio
import asyncpg

async def fix_paths():
    conn = await asyncpg.connect(
        'postgresql://postgres.lrycytjxsufexhybzkkr:6kRFCKtnvv1mlRKx@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres'
    )
    
    # Get all materials with backslashes (escape backslash in SQL)
    materials = await conn.fetch("""
        SELECT material_id, file_url 
        FROM tutor_system.sessionmaterial 
        WHERE file_url LIKE '%\\\\%'
    """)
    
    print(f"Found {len(materials)} materials with Windows paths")
    
    for material in materials:
        old_path = material['file_url']
        new_path = old_path.replace('\\', '/')
        
        print(f"\nMaterial ID {material['material_id']}:")
        print(f"  OLD: {old_path}")
        print(f"  NEW: {new_path}")
        
        # Update
        await conn.execute("""
            UPDATE tutor_system.sessionmaterial 
            SET file_url = $1 
            WHERE material_id = $2
        """, new_path, material['material_id'])
    
    print(f"\n✅ Fixed {len(materials)} file paths")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(fix_paths())
