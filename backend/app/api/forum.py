"""
Forum API
Discussion forums and community features
"""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.core.dependencies import get_current_user
from app.core.database import get_db
from app.models.database import User, Forum, ForumPost, ForumMember, Subject

router = APIRouter()


# Schemas
class CreatePostRequest(BaseModel):
    title: str
    content: str
    category: Optional[str] = "other"
    forum_id: Optional[int] = 1  # Default forum
    is_pinned: Optional[bool] = False


class CreateReplyRequest(BaseModel):
    content: str
    parent_post_id: int


@router.get("/posts")
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    subject: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get forum posts with threads - OPTIMIZED"""
    
    # OPTIMIZATION: Get posts with reply count in ONE query using LEFT JOIN and GROUP BY
    from sqlalchemy.orm import aliased
    
    ReplyPost = aliased(ForumPost)
    
    query = select(
        ForumPost,
        User,
        Forum,
        func.count(ReplyPost.post_id).label('reply_count')
    ).join(
        User, ForumPost.author_id == User.user_id
    ).join(
        Forum, ForumPost.forum_id == Forum.forum_id
    ).outerjoin(
        ReplyPost, ReplyPost.parent_post_id == ForumPost.post_id
    ).where(
        ForumPost.parent_post_id == None  # Only top-level posts (threads)
    ).group_by(
        ForumPost.post_id,
        User.user_id,
        Forum.forum_id
    ).order_by(
        ForumPost.is_pinned.desc(),
        ForumPost.created_at.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    rows = result.all()
    
    posts_list = []
    for post, author, forum, reply_count in rows:
        posts_list.append({
            "id": str(post.post_id),
            "title": post.title or "Untitled",
            "category": forum.topic or "other",
            "author": author.full_name,
            "createdAt": post.created_at.isoformat() if post.created_at else None,
            "excerpt": post.content[:200] if post.content else "",
            "likes": post.upvote_count or 0,
            "replies": reply_count or 0,
            "views": 0,  # TODO: Add view tracking
            "isPinned": post.is_pinned or False,
            "isSolved": False,  # TODO: Add solved status
            "tags": [],
            "isLiked": False
        })
    
    return posts_list


@router.get("/")
async def get_forums(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all forums"""
    
    query = select(Forum, User).join(
        User, Forum.creator_id == User.user_id
    ).where(
        Forum.is_public == True
    ).order_by(Forum.created_at.desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    forums_list = []
    for forum, creator in rows:
        forums_list.append({
            "forum_id": forum.forum_id,
            "forum_name": forum.forum_name,
            "description": forum.description,
            "topic": forum.topic,
            "creator": creator.full_name,
            "member_count": forum.member_count or 0,
            "created_at": forum.created_at.isoformat() if forum.created_at else None
        })
    
    return forums_list


@router.get("/{forum_id}/posts")
async def get_forum_posts(
    forum_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get thread detail with replies"""
    
    # Get main post
    query = select(ForumPost, User, Forum).join(
        User, ForumPost.author_id == User.user_id
    ).join(
        Forum, ForumPost.forum_id == Forum.forum_id
    ).where(
        ForumPost.post_id == forum_id
    )
    
    result = await db.execute(query)
    row = result.first()
    
    if not row:
        return {"error": "Post not found"}
    
    post, author, forum = row
    
    # Get replies
    replies_query = select(ForumPost, User).join(
        User, ForumPost.author_id == User.user_id
    ).where(
        ForumPost.parent_post_id == forum_id
    ).order_by(ForumPost.created_at.asc())
    
    replies_result = await db.execute(replies_query)
    replies_rows = replies_result.all()
    
    replies_list = []
    for reply, reply_author in replies_rows:
        replies_list.append({
            "id": str(reply.post_id),
            "author": reply_author.full_name,
            "role": reply_author.role.capitalize() if reply_author.role else "Student",
            "content": reply.content,
            "createdAt": reply.created_at.isoformat() if reply.created_at else None,
            "likes": reply.upvote_count or 0,
            "isLiked": False,
            "isAuthor": reply_author.user_id == current_user.user_id
        })
    
    return {
        "id": str(post.post_id),
        "title": post.title or "Untitled",
        "category": forum.topic or "other",
        "author": author.full_name,
        "createdAt": post.created_at.isoformat() if post.created_at else None,
        "views": 0,
        "likes": post.upvote_count or 0,
        "replies": len(replies_list),
        "isSolved": False,
        "tags": [],
        "content": post.content,
        "replies_list": replies_list
    }


@router.post("/posts")
async def create_post(
    post_data: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new forum post/thread"""
    
    # Validate forum exists
    forum_query = select(Forum).where(Forum.forum_id == post_data.forum_id)
    forum_result = await db.execute(forum_query)
    forum = forum_result.scalar_one_or_none()
    
    if not forum:
        # Create default forum if doesn't exist
        default_forum = Forum(
            forum_name="General Discussion",
            description="General discussion forum",
            topic=post_data.category or "other",
            creator_id=current_user.user_id,
            is_public=True,
            member_count=1
        )
        db.add(default_forum)
        await db.flush()
        forum = default_forum
    
    # Create the post
    user_roles = current_user.role if isinstance(current_user.role, list) else [current_user.role]
    new_post = ForumPost(
        forum_id=forum.forum_id,
        author_id=current_user.user_id,
        title=post_data.title,
        content=post_data.content,
        parent_post_id=None,  # Top-level thread
        is_pinned=post_data.is_pinned if ('admin' in user_roles or 'coordinator' in user_roles) else False,
        upvote_count=0
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    return {
        "post_id": new_post.post_id,
        "title": new_post.title,
        "content": new_post.content,
        "forum_id": new_post.forum_id,
        "author": current_user.full_name,
        "created_at": new_post.created_at.isoformat() if new_post.created_at else None,
        "message": "Post created successfully"
    }


@router.post("/{post_id}/reply")
async def create_reply(
    post_id: int,
    reply_data: CreateReplyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Reply to a forum post"""
    
    # Check if parent post exists
    parent_query = select(ForumPost).where(ForumPost.post_id == post_id)
    parent_result = await db.execute(parent_query)
    parent_post = parent_result.scalar_one_or_none()
    
    if not parent_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent post not found"
        )
    
    # Create reply
    new_reply = ForumPost(
        forum_id=parent_post.forum_id,
        author_id=current_user.user_id,
        title=None,  # Replies don't have titles
        content=reply_data.content,
        parent_post_id=post_id,
        is_pinned=False,
        upvote_count=0
    )
    
    db.add(new_reply)
    await db.commit()
    await db.refresh(new_reply)
    
    return {
        "post_id": new_reply.post_id,
        "content": new_reply.content,
        "parent_post_id": post_id,
        "author": current_user.full_name,
        "created_at": new_reply.created_at.isoformat() if new_reply.created_at else None,
        "message": "Reply created successfully"
    }
