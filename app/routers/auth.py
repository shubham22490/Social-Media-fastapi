from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm

from .. import database, models, schemas, utils, oauth2



router = APIRouter(
    tags=["Authentication"]
)

@router.post("/login", response_model=schemas.Token)
def login(user_creds: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.scalar(select(models.Users).where(models.Users.email == user_creds.username))
    
    if not user:
        # For securing from timed attacks.
        utils.verify(user_creds.password, utils.DUMMY_HASH)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")

    if not utils.verify(user_creds.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials!")

    access_token = oauth2.create_token(data = {"user_id": user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
