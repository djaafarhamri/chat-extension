from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import schemas, database
from models.user import User, friend_requests_table, friends_table
from services.auth import hash_password, verify_password, create_access_token
from datetime import timedelta
from middlewares.auth import get_current_user

router = APIRouter()

@router.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user = db.query(User).filter(User.name == user.name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="name already exist")

    new_user = User(name=user.name, password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user 

@router.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(User).filter(User.name == user.name).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user.name, "user_id": db_user.id}, timedelta(minutes=60*24))
    return {"access_token": token, "token_type": "bearer"}

@router.get("/get_users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(database.get_db)):
    users = db.query(User).all()
    return users

# send friend request
@router.post("/send_friend_request/{receiver_id}")
def send_friend_request(receiver_id: int, db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    sender_id = current_user.id
    if sender_id == receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send a friend request to yourself")

    sender = db.query(User).filter(User.id == sender_id).first()
    receiver = db.query(User).filter(User.id == receiver_id).first()
    
    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if request already exists
    existing_request = db.execute(
        friend_requests_table.select().where(
            (friend_requests_table.c.sender_id == sender_id) &
            (friend_requests_table.c.receiver_id == receiver_id)
        )
    ).fetchone()

    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")

    # Insert new request
    db.execute(friend_requests_table.insert().values(sender_id=sender_id, receiver_id=receiver_id))
    db.commit()

    return {"message": "Friend request sent"}


@router.post("/accept_friend_request/{sender_id}")
def accept_friend_request(sender_id: int, db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    receiver_id = current_user.id
    # Ensure the request exists
    existing_request = db.execute(
        friend_requests_table.select().where(
            (friend_requests_table.c.sender_id == sender_id) &
            (friend_requests_table.c.receiver_id == receiver_id)
        )
    ).fetchone()

    if not existing_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    # Delete friend request
    db.execute(
        friend_requests_table.delete().where(
            (friend_requests_table.c.sender_id == sender_id) &
            (friend_requests_table.c.receiver_id == receiver_id)
        )
    )

    # Add to friends table (bidirectional)
    db.execute(friends_table.insert().values(user_id=sender_id, friend_id=receiver_id))
    db.execute(friends_table.insert().values(user_id=receiver_id, friend_id=sender_id))

    db.commit()
    return {"message": "Friend request accepted"}

# **Reject a friend request**
@router.delete("/reject_friend_request/{sender_id}")
def reject_friend_request(sender_id: int, db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    receiver_id = current_user.id
    # Check if the friend request exists
    existing_request = db.execute(
        friend_requests_table.select().where(
            (friend_requests_table.c.sender_id == sender_id) &
            (friend_requests_table.c.receiver_id == receiver_id)
        )
    ).fetchone()

    if not existing_request:
        raise HTTPException(status_code=404, detail="Friend request not found")

    # Delete friend request
    db.execute(
        friend_requests_table.delete().where(
            (friend_requests_table.c.sender_id == sender_id) &
            (friend_requests_table.c.receiver_id == receiver_id)
        )
    )
    db.commit()

    return {"message": "Friend request rejected"}

# Get user friends
@router.get("/user/{user_id}/friends")
def get_friends(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"friends": [friend.name for friend in user.friends]}

# Get my friends
@router.get("/my_friends")
def get_friends(db: Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "friends": [{"id": friend.id, "name": friend.name} for friend in user.friends],
        "friendRequests": [{"id": friend.id, "name": friend.name} for friend in user.friend_requests]
        }

@router.get("/sent_friend_requests/{user_id}")
def get_sent_friend_requests(user_id: int, db: Session = Depends(database.get_db)):
    sent_requests = db.execute(
        friend_requests_table.select().where(friend_requests_table.c.sender_id == user_id)
    ).fetchall()

    return {"sent_requests": [{"receiver_id": req.receiver_id} for req in sent_requests]}

@router.get("/received_friend_requests/{user_id}")
def get_received_friend_requests(user_id: int, db: Session = Depends(database.get_db)):
    received_requests = db.execute(
        friend_requests_table.select().where(friend_requests_table.c.receiver_id == user_id)
    ).fetchall()

    return {"received_requests": [{"sender_id": req.sender_id} for req in received_requests]}

@router.delete("/remove_friend/{friend_id}")
def removeFriend(friend_id: int, db : Session = Depends(database.get_db), current_user: User = Depends(get_current_user)):
    # Check if the friend request exists
    print(friend_id, current_user.id)
    isFriend = db.execute(
        friends_table.select().where(
            (friends_table.c.user_id == current_user.id) &
            (friends_table.c.friend_id == friend_id)
        )
    ).fetchone()

    if not isFriend:
        raise HTTPException(status_code=404, detail="not a friend")

    # Delete friend request
    db.execute(
        friends_table.delete().where(
            (friends_table.c.user_id == current_user.id) &
            (friends_table.c.friend_id == friend_id) 
        )
    )
    db.execute(
        friends_table.delete().where(
            (friends_table.c.friend_id == current_user.id) &
            (friends_table.c.user_id == friend_id) 
        )
    )
    db.commit()

    return {"message": "Friend removed"}