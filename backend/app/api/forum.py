"""Forum API — thin controller, delegates to ForumService"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.core.dependencies import get_current_user, get_forum_service
from app.models.database import User
from app.services.forum_service import ForumService
from app.schemas.forum import CreatePostRequest, CreateReplyRequest

router = APIRouter()

# --- Routes ---
@router.get("/posts")
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100),
    svc: ForumService = Depends(get_forum_service),
):
    return await svc.get_posts(skip, limit)

@router.get("/")
async def get_forums(
    current_user: User = Depends(get_current_user),
    svc: ForumService = Depends(get_forum_service),
):
    return await svc.get_forums()

@router.get("/{forum_id}/posts")
async def get_forum_posts(
    forum_id: int,
    current_user: User = Depends(get_current_user),
    svc: ForumService = Depends(get_forum_service),
):
    return await svc.get_thread(forum_id, current_user.user_id)

@router.post("/posts")
async def create_post(
    post_data: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    svc: ForumService = Depends(get_forum_service),
):
    return await svc.create_post(
        current_user, post_data.title, post_data.content,
        post_data.category, post_data.forum_id, post_data.is_pinned)

@router.post("/{post_id}/reply")
async def create_reply(
    post_id: int,
    reply_data: CreateReplyRequest,
    current_user: User = Depends(get_current_user),
    svc: ForumService = Depends(get_forum_service),
):
    return await svc.create_reply(current_user, post_id, reply_data.content)
