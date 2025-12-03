"""
Test Materials API after migration to database storage
"""
import asyncio
import asyncpg

async def test_migration():
    conn = await asyncpg.connect(
        'postgresql://postgres.lrycytjxsufexhybzkkr:6kRFCKtnvv1mlRKx@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres'
    )
    
    print("=" * 60)
    print("TESTING MATERIALS MIGRATION")
    print("=" * 60)
    
    # 1. Check column exists
    print("\n1️⃣  Checking file_data column...")
    column_exists = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'tutor_system'
            AND table_name = 'sessionmaterial'
            AND column_name = 'file_data'
        )
    """)
    print(f"   ✅ file_data column exists: {column_exists}")
    
    # 2. Check file_url is nullable
    print("\n2️⃣  Checking file_url nullable...")
    is_nullable = await conn.fetchval("""
        SELECT is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'tutor_system'
        AND table_name = 'sessionmaterial'
        AND column_name = 'file_url'
    """)
    print(f"   ✅ file_url is nullable: {is_nullable == 'YES'}")
    
    # 3. Count materials
    print("\n3️⃣  Checking existing materials...")
    stats = await conn.fetchrow("""
        SELECT 
            COUNT(*) as total,
            COUNT(file_data) as in_db,
            COUNT(file_url) as on_disk,
            SUM(CASE WHEN file_data IS NOT NULL THEN 1 ELSE 0 END) as new_format,
            SUM(CASE WHEN file_data IS NULL AND file_url IS NOT NULL THEN 1 ELSE 0 END) as legacy_format
        FROM tutor_system.sessionmaterial
    """)
    
    print(f"   Total materials: {stats['total']}")
    print(f"   New format (in DB): {stats['new_format']}")
    print(f"   Legacy format (on disk): {stats['legacy_format']}")
    
    # 4. Show recent materials
    print("\n4️⃣  Recent materials (5 latest):")
    materials = await conn.fetch("""
        SELECT 
            material_id,
            session_id,
            file_name,
            file_size,
            CASE 
                WHEN file_data IS NOT NULL THEN 'DATABASE'
                WHEN file_url IS NOT NULL THEN 'DISK (legacy)'
                ELSE 'MISSING'
            END as storage_type,
            uploaded_at
        FROM tutor_system.sessionmaterial
        ORDER BY uploaded_at DESC
        LIMIT 5
    """)
    
    for m in materials:
        print(f"   ID {m['material_id']}: {m['file_name']} ({m['file_size']} bytes)")
        print(f"      Storage: {m['storage_type']}, Uploaded: {m['uploaded_at']}")
    
    # 5. Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    if column_exists and is_nullable == 'YES':
        print("✅ Migration successful!")
        print(f"✅ Ready to upload files to database")
        print(f"✅ Backward compatible with {stats['legacy_format']} legacy files")
    else:
        print("❌ Migration incomplete!")
        if not column_exists:
            print("   - file_data column missing")
        if is_nullable != 'YES':
            print("   - file_url should be nullable")
    
    print("\n📝 Next steps:")
    print("   1. Upload a new file to test")
    print("   2. Verify file_data column has binary data")
    print("   3. Download file to confirm it works")
    print("   4. Delete test file")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(test_migration())
