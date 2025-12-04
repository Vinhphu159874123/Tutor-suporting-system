import asyncio
import asyncpg

async def check_material():
    conn = await asyncpg.connect(
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        port=6543,
        user="postgres.ilnlulcvbebfsxjuqgvm",
        password="Vinhphu1598741%23",  # URL encoded #
        database="postgres"
    )
    
    result = await conn.fetch("""
        SELECT material_id, title, file_url, file_type, file_size,
               CASE WHEN file_data IS NOT NULL THEN length(file_data) ELSE 0 END as data_bytes
        FROM tutor_system.studygroupmaterial
        WHERE group_id = 5
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    print(f"Found {len(result)} material(s) in group 5:")
    print("=" * 80)
    for row in result:
        print(f"\nMaterial ID: {row['material_id']}")
        print(f"Title: {row['title']}")
        print(f"URL: {row['file_url']}")
        print(f"Type: {row['file_type']}")
        print(f"Size: {row['file_size']} bytes" if row['file_size'] else "Size: None")
        print(f"Data in DB: {row['data_bytes']} bytes {'✅' if row['data_bytes'] > 0 else '❌ MISSING'}")
    
    await conn.close()

asyncio.run(check_material())
