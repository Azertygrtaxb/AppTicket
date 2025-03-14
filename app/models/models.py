# coding: utf-8
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    hashpassword = Column(String(255), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(Enum('user', 'technician', 'admin'), nullable=False, server_default=text("'user'"))
    phone_number = Column(String(15))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    is_active = Column(TINYINT(1), server_default=text("'1'"))


class Category(Base):
    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text, nullable=False)


class Ticket(Base):
    __tablename__ = 'tickets'

    ticket_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum('ouvert', 'en cours', 'resolu', 'ferme'), server_default=text("'ouvert'"))
    priority = Column(Enum('faible', 'moyenne', 'elevee', 'critique'), server_default=text("'moyenne'"))
    category_id = Column(ForeignKey('categories.category_id', ondelete='SET NULL'), index=True)
    created_by = Column(ForeignKey('Users.user_id', ondelete='CASCADE'), index=True)
    assigned_to = Column(ForeignKey('Users.user_id', ondelete='SET NULL'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    User = relationship('User', primaryjoin='Ticket.assigned_to == User.user_id')
    category = relationship('Category')
    User1 = relationship('User', primaryjoin='Ticket.created_by == User.user_id')


class KnowledgeBase(Base):
    __tablename__ = 'knowledge_base'

    article_id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    keyword = Column(Text, nullable=False)
    category_id = Column(ForeignKey('categories.category_id', ondelete='CASCADE'), nullable=False, index=True)
    source_ticket_id = Column(ForeignKey('tickets.ticket_id', ondelete='SET NULL'), index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    category = relationship('Category')
    source_ticket = relationship('Ticket')


class Notification(Base):
    __tablename__ = 'notifications'

    notification_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    ticket_id = Column(ForeignKey('tickets.ticket_id', ondelete='CASCADE'), nullable=False, index=True)
    message = Column(Text)
    is_read = Column(TINYINT(1), server_default=text("'0'"))
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    ticket = relationship('Ticket')
    user = relationship('User')


class TicketComment(Base):
    __tablename__ = 'ticket_comments'

    comment_id = Column(Integer, primary_key=True)
    ticket_id = Column(ForeignKey('tickets.ticket_id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(ForeignKey('Users.user_id', ondelete='CASCADE'), nullable=False, index=True)
    comment = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    ticket = relationship('Ticket')
    user = relationship('User')


class TicketDependency(Base):
    __tablename__ = 'ticket_dependencies'

    parent_ticket_id = Column(ForeignKey('tickets.ticket_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    child_ticket_id = Column(ForeignKey('tickets.ticket_id', ondelete='CASCADE'), primary_key=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    child_ticket = relationship('Ticket', primaryjoin='TicketDependency.child_ticket_id == Ticket.ticket_id')
    parent_ticket = relationship('Ticket', primaryjoin='TicketDependency.parent_ticket_id == Ticket.ticket_id')
