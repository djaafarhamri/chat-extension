from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.chat import Chat
from models.user import User, friends_table
from db.schemas import MessageSend
from middlewares.auth import get_current_user

router = APIRouter()

# Send a message
@router.post("/send_message/{receiver_id}")
def send_message(receiver_id: int, chat: MessageSend, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id == receiver_id:
        raise HTTPException(status_code=400, detail="cant send message to oneself")    
    sender = db.query(User).filter(User.id == current_user.id).first()
    receiver = db.query(User).filter(User.id == receiver_id).first()
    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="User not found")
   # Check if sender and receiver are friends
    is_friend = db.execute(
        friends_table.select().where(
            ((friends_table.c.user_id == sender.id) & (friends_table.c.friend_id == receiver.id)) |
            ((friends_table.c.user_id == receiver.id) & (friends_table.c.friend_id == sender.id))
        )
    ).fetchone()

    if not is_friend:
        raise HTTPException(status_code=403, detail="You can only send messages to friends")

    chat_message = Chat(sender_id=current_user.id, receiver_id=receiver_id, message=chat.message)
    db.add(chat_message)
    db.commit()
    return {"message": "Message sent successfully"}

# Get chat history
@router.get("/chat/{user1_id}/{user2_id}")
def get_chat(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    chats = (
        db.query(Chat)
        .filter(
            ((Chat.sender_id == user1_id) & (Chat.receiver_id == user2_id)) |
            ((Chat.sender_id == user2_id) & (Chat.receiver_id == user1_id))
        )
        .order_by(Chat.timestamp)
        .all()
    )
    
    return {"chat_history": [{"sender": c.sender_id, "receiver": c.receiver_id, "message": c.message, "timestamp": c.timestamp} for c in chats]}
