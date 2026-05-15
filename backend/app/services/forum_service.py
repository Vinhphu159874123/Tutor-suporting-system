"""
Forum Service — business logic for discussion forums
"""
from typing import List, Dict, Any
from fastapi import HTTPException
from app.models.database import User, Forum, ForumPost
from app.repositories.forum_repository import ForumRepository
from app.core.cache import get_or_load


class ForumService:
    def __init__(self, repo: ForumRepository):
        self.repo = repo

    async def get_posts(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        async def _load():
            rows = await self.repo.get_posts_with_authors(skip, limit)
            return [
                {"id": str(p.post_id), "title": p.title or "Untitled",
                 "category": f.topic or "other", "author": u.full_name,
                 "createdAt": p.created_at.isoformat() if p.created_at else None,
                 "excerpt": p.content[:200] if p.content else "",
                 "likes": p.upvote_count or 0, "replies": rc or 0, "views": 0,
                 "isPinned": p.is_pinned or False, "isSolved": False,
                 "tags": [], "isLiked": False}
                for p, u, f, rc in rows
            ]
        return await get_or_load(f"forum:posts:{skip}:{limit}", _load, ttl=20)

    async def get_forums(self) -> List[Dict[str, Any]]:
        rows = await self.repo.get_public_forums()
        return [{"forum_id": f.forum_id, "forum_name": f.forum_name,
                 "description": f.description, "topic": f.topic,
                 "creator": u.full_name, "member_count": f.member_count or 0,
                 "created_at": f.created_at.isoformat() if f.created_at else None}
                for f, u in rows]

    async def get_thread(self, post_id: int, current_user_id: int) -> Dict[str, Any]:
        row = await self.repo.get_post_with_details(post_id)
        if not row:
            raise HTTPException(status_code=404, detail="Post not found")
        post, author, forum = row
        replies_rows = await self.repo.get_replies(post_id)
        replies_list = []
        for reply, ra in replies_rows:
            role = ra.role[0] if isinstance(ra.role, list) and ra.role else (
                ra.role if isinstance(ra.role, str) else "student")
            replies_list.append({"id": str(reply.post_id), "author": ra.full_name,
                                 "role": role.capitalize(), "content": reply.content,
                                 "createdAt": reply.created_at.isoformat() if reply.created_at else None,
                                 "likes": reply.upvote_count or 0, "isLiked": False,
                                 "isAuthor": ra.user_id == current_user_id})
        return {"id": str(post.post_id), "title": post.title or "Untitled",
                "category": forum.topic or "other", "author": author.full_name,
                "createdAt": post.created_at.isoformat() if post.created_at else None,
                "views": 0, "likes": post.upvote_count or 0,
                "replies": len(replies_list), "isSolved": False, "tags": [],
                "content": post.content, "replies_list": replies_list}

    async def create_post(self, user: User, title: str, content: str,
                          category: str = "other", forum_id: int = 1,
                          is_pinned: bool = False) -> Dict[str, Any]:
        fr = await self.repo.get_forum_by_id(forum_id)
        if not fr:
            fr = Forum(forum_name="General Discussion", description="General discussion forum",
                       topic=category, creator_id=user.user_id, is_public=True, member_count=1)
            fr = await self.repo.create_forum(fr)
        roles = user.role if isinstance(user.role, list) else [user.role]
        pin = is_pinned if ('admin' in roles or 'coordinator' in roles) else False
        new_post = ForumPost(forum_id=fr.forum_id, author_id=user.user_id,
                             title=title, content=content, parent_post_id=None,
                             is_pinned=pin, upvote_count=0)
        try:
            new_post = await self.repo.create_post(new_post)
        except Exception:
            raise
        return {"post_id": new_post.post_id, "title": new_post.title,
                "content": new_post.content, "forum_id": new_post.forum_id,
                "author": user.full_name,
                "created_at": new_post.created_at.isoformat() if new_post.created_at else None,
                "message": "Post created successfully"}

    async def create_reply(self, user: User, post_id: int, content: str) -> Dict[str, Any]:
        parent = await self.repo.get_post_by_id(post_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent post not found")
        reply = ForumPost(forum_id=parent.forum_id, author_id=user.user_id,
                          title=None, content=content, parent_post_id=post_id,
                          is_pinned=False, upvote_count=0)
        try:
            reply = await self.repo.create_post(reply)
        except Exception:
            raise
        return {"post_id": reply.post_id, "content": reply.content,
                "parent_post_id": post_id, "author": user.full_name,
                "created_at": reply.created_at.isoformat() if reply.created_at else None,
                "message": "Reply created successfully"}
