"""
Forum Service - Business Logic Layer
"""
from typing import List, Optional
from app.repositories.forum_repository import ForumRepository


class ForumService:
    """Handle forum business logic"""
    
    def __init__(self, forum_repo: ForumRepository):
        self.forum_repo = forum_repo
    
    async def get_posts(self, skip: int = 0, limit: int = 20) -> List:
        """Get forum posts"""
        return await self.forum_repo.get_posts(skip, limit)
    
    async def create_post(self, post_data: dict, user_id: int) -> dict:
        """Create new forum post"""
        return await self.forum_repo.create_post(post_data, user_id)
    
    async def add_comment(self, post_id: int, comment_data: dict, user_id: int) -> dict:
        """Add comment to post"""
        return await self.forum_repo.add_comment(post_id, comment_data, user_id)
    
    async def vote_post(self, post_id: int, user_id: int, vote_type: str) -> dict:
        """Vote on post (upvote/downvote)"""
        return await self.forum_repo.vote_post(post_id, user_id, vote_type)
