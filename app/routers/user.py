from .. import models, schemas, utils, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import select, insert, delete, update


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    user.password = utils.hash(user.password)
    print(user.model_dump())
    
    new_user = db.scalar(insert(models.Users).returning(models.Users), user.model_dump())
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), user_id: schemas.TokenData = Depends(oauth2.get_current_user)):
    user = db.scalar(select(models.Users).where(models.Users.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with id: {id} not found.")
    return user