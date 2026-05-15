"""
Forum Repository
Database operations for Forum and ForumPost models
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import aliased
from typing import List, Optional, Any
from app.models.database import User, Forum, ForumPost


class ForumRepository:
    """Handle all database operations for Forum/ForumPost models"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_posts_with_authors(self, skip: int = 0, limit: int = 100) -> list:
        ReplyPost = aliased(ForumPost)
        query = (select(ForumPost, User, Forum,
                        func.count(ReplyPost.post_id).label('reply_count'))
                 .join(User, ForumPost.author_id == User.user_id)
                 .join(Forum, ForumPost.forum_id == Forum.forum_id)
                 .outerjoin(ReplyPost, ReplyPost.parent_post_id == ForumPost.post_id)
                 .where(ForumPost.parent_post_id == None)
                 .group_by(ForumPost.post_id, User.user_id, Forum.forum_id)
                 .order_by(ForumPost.is_pinned.desc(), ForumPost.created_at.desc())
                 .offset(skip).limit(limit))
        return (await self.db.execute(query)).all()

    async def get_public_forums(self) -> list:
        return (await self.db.execute(
            select(Forum, User).join(User, Forum.creator_id == User.user_id)
            .where(Forum.is_public == True).order_by(Forum.created_at.desc())
        )).all()

    async def get_post_with_details(self, post_id: int):
        return (await self.db.execute(
            select(ForumPost, User, Forum)
            .join(User, ForumPost.author_id == User.user_id)
            .join(Forum, ForumPost.forum_id == Forum.forum_id)
            .where(ForumPost.post_id == post_id)
        )).first()

    async def get_replies(self, post_id: int) -> list:
        return (await self.db.execute(
            select(ForumPost, User).join(User, ForumPost.author_id == User.user_id)
            .where(ForumPost.parent_post_id == post_id)
            .order_by(ForumPost.created_at.asc())
        )).all()

    async def get_forum_by_id(self, forum_id: int) -> Optional[Forum]:
        return (await self.db.execute(
            select(Forum).where(Forum.forum_id == forum_id)
        )).scalar_one_or_none()

    async def create_forum(self, forum: Forum) -> Forum:
        self.db.add(forum)
        await self.db.flush()
        return forum

    async def create_post(self, post: ForumPost) -> ForumPost:
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def get_post_by_id(self, post_id: int) -> Optional[ForumPost]:
        return (await self.db.execute(
            select(ForumPost).where(ForumPost.post_id == post_id)
        )).scalar_one_or_none()
