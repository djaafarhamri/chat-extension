from fastapi import FastAPI
from db.database import Base, engine
from routes import user, chat

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)
# Include API routes
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(chat.router, prefix="/chats", tags=["Chats"])
