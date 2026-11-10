from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, database, oauth2, models
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), user = Depends(oauth2.get_current_user)):
    post = db.scalar(select(models.Post).where(models.Post.id == vote.post_id))
    if (post is None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with {vote.post_id} not found!")

    vote_query = select(models.Votes).where(models.Votes.post_id == vote.post_id, models.Votes.user_id == user.id)
    existing_vote = db.scalar(vote_query)

    if(vote.dir):
        if(existing_vote is not None):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Vote for post {vote.post_id} already exists!")
        vote_data = models.Votes(post_id=vote.post_id, user_id=user.id)
        db.add(vote_data)
        db.commit()

        return {"message": f"Vote for post {vote.post_id} added succesfully!"}

    else: 
        if(existing_vote is None):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote for post {vote.post_id} doesn't found!")

        db.delete(existing_vote)
        db.commit()

        return {"message": f"Vote for post {vote.post_id} deleted succesfully!"}

