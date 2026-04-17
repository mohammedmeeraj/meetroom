from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas.room import RoomOut, RoomCreate
from typing import Annotated
from app.database import get_db
from sqlalchemy.orm import Session
from livekit import api as livekit_api
from app.models.user import User
from app.models.room import Room
from app.core.security import get_current_active_user
from app.dependencies import get_settings
import asyncio
from datetime import datetime, timezone


settings = get_settings()

router = APIRouter(prefix="/rooms", tags=["rooms"])

async def _delete_livekit_room(slug: str):
    """
    Tell LiveKit to delete the room — this disconnects all participants immediately.
    """
    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        return
    try:
        lkapi = livekit_api.LiveKitAPI(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
        )
        await lkapi.room.delete_room(livekit_api.DeleteRoomRequest(room=slug))
        await lkapi.aclose()
    except Exception:
        pass  # Non-fatal — DB is already marked ended

@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(
    payload: RoomCreate,
    db: Annotated[Session, Depends(get_db)],
    current_active_user: Annotated[User, Depends(get_current_active_user)]
):
    """Create a new meeting room. Returns the room including its shareable slug."""
    room = Room(
        name=payload.name.strip(),
        host_id=current_active_user.id,
    )

    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@router.get("", response_model=list[RoomOut])
def list_rooms(
    db: Annotated[Session, Depends(get_db)],
    current_active_user: Annotated[User, Depends(get_current_active_user)],  
):
    """List all rooms created by the authenticated host, newest first."""
    return (
        db.query(Room)
        .filter(Room.host_id == current_active_user.id)
        .order_by(Room.created_at.desc())
        .all()
    )

@router.get("/{slug}", response_model=RoomOut)
def get_room(slug: str, db: Annotated[Session, Depends(get_db)]):
    """
    Get room info by slug. Public endpoint — used by guests
    to verify a room exists before joining.
    """
    room = db.query(Room).filter(Room.slug == slug).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room


@router.patch("/{slug}/end", response_model=RoomOut)
async def end_room(
    slug: str,
    db: Annotated[Session, Depends(get_db)],
    current_active_user: Annotated[User, Depends(get_current_active_user)],  
    
):
    """
    Mark a room as ended and immediately kick all LiveKit participants.
    Only the host can end their own room.
    """
    room = db.query(Room).filter(Room.slug == slug).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    if room.host_id != current_active_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the host can end this room")

    room.is_active = False
    room.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(room)

    # Kick everyone from LiveKit 
    asyncio.create_task(_delete_livekit_room(slug))

    return room

@router.get("/{slug}/participants")
async def get_participants(slug: str, db: Annotated[Session, Depends(get_db)]):
    """
    Return the live participant count for a room from LiveKit.
    Public endpoint — used by the dashboard to show live guest counts.
    """
    room = db.query(Room).filter(Room.slug == slug).first()
    if not room or not room.is_active:
        return {"count": 0, "participants": []}

    if not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        return {"count": 0, "participants": []}

    try:
        lkapi = livekit_api.LiveKitAPI(
            settings.LIVEKIT_URL,
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET,
        )
        resp = await lkapi.room.list_participants(
            livekit_api.ListParticipantsRequest(room=slug)
        )
        await lkapi.aclose()
        names = [p.name or p.identity.split("#")[0] for p in resp.participants]
        return {"count": len(names), "participants": names}
    except Exception:
        return {"count": 0, "participants": []}
