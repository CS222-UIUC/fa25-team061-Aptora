from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, AvailabilitySlot
from ..schemas import AvailabilitySlotCreate, AvailabilitySlotUpdate, AvailabilitySlot as AvailabilitySlotSchema
from ..auth import current_active_user

router = APIRouter(prefix="/availability", tags=["availability"])


@router.post("/", response_model=AvailabilitySlotSchema)
async def create_availability_slot(
    availability: AvailabilitySlotCreate,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new availability slot."""
    db_availability = AvailabilitySlot(**availability.dict(), user_id=current_user.id)
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability


@router.get("/", response_model=List[AvailabilitySlotSchema])
async def get_availability_slots(
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get all availability slots for the current user."""
    slots = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.user_id == current_user.id
    ).all()
    return slots


@router.get("/{slot_id}", response_model=AvailabilitySlotSchema)
async def get_availability_slot(
    slot_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific availability slot by ID."""
    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == slot_id,
        AvailabilitySlot.user_id == current_user.id
    ).first()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability slot not found"
        )
    
    return slot


@router.put("/{slot_id}", response_model=AvailabilitySlotSchema)
async def update_availability_slot(
    slot_id: int,
    availability_update: AvailabilitySlotUpdate,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Update an availability slot."""
    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == slot_id,
        AvailabilitySlot.user_id == current_user.id
    ).first()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability slot not found"
        )
    
    for field, value in availability_update.dict(exclude_unset=True).items():
        setattr(slot, field, value)
    
    db.commit()
    db.refresh(slot)
    return slot


@router.delete("/{slot_id}")
async def delete_availability_slot(
    slot_id: int,
    current_user: User = Depends(current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an availability slot."""
    slot = db.query(AvailabilitySlot).filter(
        AvailabilitySlot.id == slot_id,
        AvailabilitySlot.user_id == current_user.id
    ).first()
    
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability slot not found"
        )
    
    db.delete(slot)
    db.commit()
    return {"message": "Availability slot deleted successfully"}
