from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas.room import RoomOut, RoomCreate
from typing import Annotated
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.room import Room
from app.core.security import get_current_active_user

router = APIRouter(prefix="/rooms", tags=["rooms"])

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