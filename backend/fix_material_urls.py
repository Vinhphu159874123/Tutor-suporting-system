import asyncio
from sqlalchemy import text
from app.core.database import engine

async def fix_materials():
    async with engine.begin() as conn:
        # Update URLs
        await conn.execute(text("""
            UPDATE tutor_system.studygroupmaterial 
            SET file_url = '/api/v1/study-groups/' || group_id || '/materials/' || material_id
            WHERE file_data IS NOT NULL
        """))
        
        # Check results
        result = await conn.execute(text("""
            SELECT material_id, title, file_url, 
                   CASE WHEN file_data IS NOT NULL THEN 'Yes' ELSE 'No' END as has_file
            FROM tutor_system.studygroupmaterial 
            ORDER BY material_id
        """))
        
        print('✅ Updated material URLs:')
        for row in result:
            print(f'  ID {row[0]}: {row[1]} -> {row[2]} (File: {row[3]})')

if __name__ == "__main__":
    asyncio.run(fix_materials())
