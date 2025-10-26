"""
Student Repository - Database Access Layer
Pure database operations, no business logic
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.models.database import Student


class StudentRepository:
    """Handle database operations for Student model"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, student_id: int) -> Optional[Student]:
        """Get student by ID"""
        result = await self.db.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user_id(self, user_id: int) -> Optional[Student]:
        """Get student by user ID"""
        result = await self.db.execute(
            select(Student).where(Student.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        year: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[Student]:
        """Get all students with optional filters"""
        query = select(Student)
        
        if year is not None:
            query = query.where(Student.year == year)
        
        if is_active is not None:
            query = query.where(Student.is_active == is_active)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, student_data: dict) -> Student:
        """Create new student"""
        student = Student(**student_data)
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student
    
    async def update(self, student_id: int, student_data: dict) -> Optional[Student]:
        """Update student"""
        student = await self.get_by_id(student_id)
        if not student:
            return None
        
        for key, value in student_data.items():
            setattr(student, key, value)
        
        await self.db.commit()
        await self.db.refresh(student)
        return student
    
    async def delete(self, student_id: int) -> bool:
        """Delete student (hard delete)"""
        student = await self.get_by_id(student_id)
        if not student:
            return False
        
        await self.db.delete(student)
        await self.db.commit()
        return True
    
    async def exists_by_user_id(self, user_id: int) -> bool:
        """Check if user already has student profile"""
        result = await self.db.execute(
            select(Student.id).where(Student.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None
