from sqlalchemy import Column, Integer, String, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from db.database import Base

# Association table for friends (self-referential many-to-many)
friends_table = Table(
    "friends",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("friend_id", Integer, ForeignKey("users.id"), primary_key=True),
)
# Association table for friends (self-referential many-to-many)
friend_requests_table = Table(
    "friend_requests",
    Base.metadata,
    Column("sender_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("receiver_id", Integer, ForeignKey("users.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    # Many-to-many self-referential relationship for accepted friends
    friends = relationship(
        "User",
        secondary=friends_table,
        primaryjoin=id == friends_table.c.user_id,
        secondaryjoin=id == friends_table.c.friend_id,
        backref="friend_of",
    )

    # Many-to-many self-referential relationship for pending friend requests
    friend_requests = relationship(
        "User",
        secondary=friend_requests_table,
        primaryjoin=id == friend_requests_table.c.sender_id,
        secondaryjoin=id == friend_requests_table.c.receiver_id,
        backref="pending_requests",
    )
