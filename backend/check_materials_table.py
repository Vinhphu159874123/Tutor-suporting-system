"""
Script to check if sessionmaterial table exists and has data
"""
import asyncio
import asyncpg
import sys

async def check_materials_table():
    """Check sessionmaterial table in Supabase"""
    
    # Connection string
    conn_string = "postgresql://postgres.lrycytjxsufexhybzkkr:6kRFCKtnvv1mlRKx@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"
    
    try:
        # Connect to database
        conn = await asyncpg.connect(conn_string)
        print("✅ Connected to Supabase database\n")
        
        # Check if table exists
        table_exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'tutor_system' 
                AND table_name = 'sessionmaterial'
            );
        """)
        
        if table_exists:
            print("✅ Table 'tutor_system.sessionmaterial' EXISTS\n")
            
            # Get table structure
            print("📋 Table Structure:")
            columns = await conn.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'tutor_system'
                AND table_name = 'sessionmaterial'
                ORDER BY ordinal_position;
            """)
            
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']})")
            
            # Count records
            count = await conn.fetchval("SELECT COUNT(*) FROM tutor_system.sessionmaterial")
            print(f"\n📊 Total records: {count}")
            
            # Show recent uploads (if any)
            if count > 0:
                print("\n📁 Recent uploads:")
                materials = await conn.fetch("""
                    SELECT material_id, session_id, file_name, file_size, uploaded_at, uploaded_by
                    FROM tutor_system.sessionmaterial
                    ORDER BY uploaded_at DESC
                    LIMIT 5
                """)
                
                for m in materials:
                    print(f"  ID: {m['material_id']} | Session: {m['session_id']} | File: {m['file_name']} | Size: {m['file_size']} bytes | Uploaded: {m['uploaded_at']}")
            else:
                print("\n⚠️  No materials uploaded yet")
                
        else:
            print("❌ Table 'tutor_system.sessionmaterial' DOES NOT EXIST")
            print("\n🔧 Need to run migration:")
            print("   psql <connection_string> -f backend/migrations/create_sessionmaterial_table.sql")
            print("   OR run the SQL in Supabase SQL Editor")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(check_materials_table())
