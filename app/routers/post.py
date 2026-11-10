from .. import models, schemas, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

from sqlalchemy.orm import Session
from ..database import get_db
from sqlalchemy import func, select, insert, delete, update


from typing import List

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# @router.get("/", response_model=List[schemas.PostOutput])
@router.get("/", response_model=List[schemas.PostOutput])
def get_posts(limit: int = 10, skip: int = 0, search: str = "", db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    stmt = (
        select(
            models.Post,
            func.count(models.Votes.user_id).label("votes"),
        )
        .outerjoin(
            models.Votes,
            models.Post.id == models.Votes.post_id
        )
        .where(models.Post.title.contains(search))
        .group_by(models.Post.id)
        .limit(limit)
        .offset(skip)
    )

    result = db.execute(stmt).all()

    return [
        {"post": post, "votes": vote_count}
        for post, vote_count in result
    ]

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOutput)
def create_post(post: schemas.PostInput, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # NEVER do this can have SQL INJECTION.
    # cursor.execute("""INSERT INTO posts(title, content, published) VALUES ({post.title}, {posts.content}, {post.published})""")
    # cursor.execute("""INSERT INTO posts(title, content, published) VALUES (%s, %s, %s) RETURNING *""", (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    # print(post.model_dump())

    # new_post = db.scalar(insert(models.Post).returning(models.Post), post.model_dump())
    print(current_user.id)
    new_post = models.Post(owner_id = current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get("/{id}", response_model=schemas.PostOutput)
def get_post(id: int, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    # post = cursor.fetchone()
    # post = db.get(models.Post, id)

    result = db.execute(
        select(
            models.Post,
            func.count(models.Votes.user_id).label("votes")
        )
        .outerjoin(
            models.Votes, 
            models.Post.id == models.Votes.post_id
        )
        .where(models.Post.id == id)
        .group_by(models.Post.id)
    ).first()

    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found.")
    
    post, vote_count = result
    return {"post": post, "votes": vote_count}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db:Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (id,))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.get(models.Post, id)
    print(post)
    if(post == None):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist.")
    
    if(post.owner_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action!")
    
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostOutput)
def update_post(id: int, post: schemas.PostInput, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()

    stmt = (
            update(models.Post)
            .where(models.Post.id == id)
            .values(**post.model_dump())
            .returning(models.Post)
        )

    updated_post = db.scalar(stmt)

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id: {id} does not exists.")

    if(updated_post.owner_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action!")
        
    db.commit()
    db.refresh(updated_post)
    return updated_post
