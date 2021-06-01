
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime
)

# связующий класс Base. От него наследуются все классы (таблицы), относящиеся к этой базе данных!
Base = declarative_base()

#Создадим классы Миксины - Id, Url, Name

class IdMixin():
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

class UrlMixin():
    url = Column(String(2048), nullable = False, unique = True)

class NameMixin():
    name = Column(String(200), nullable = False, unique = False)

#Классы (таблицы), относящиеся к базе данных Base (наследуются от него)

#Вспомогательный класс для реализации связи many to many между постами и тегами
#т.к. одни и те же теги могут быть в разных постах

posts_tags = Table(
    'posts_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id')))

class Post(Base, IdMixin, UrlMixin):
    __tablename__ = 'post'
    title = Column(String, nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey("author.id"), nullable=False)
    image = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, nullable=False)
    author = relationship("Author", backref="posts")
    tags = relationship("Tag", secondary=posts_tags)


class Author(Base, IdMixin, UrlMixin, NameMixin):
    __tablename__ = 'author'

class Comments(Base, IdMixin, UrlMixin):
    __tablename__ = 'comments'
    text = Column(String(2048))
    created_at = Column(DateTime, )
    likes_count = Column(Integer)
    Column(DateTime, nullable=False)
    # ранее выводили отдельно имя и фамилию автора, сейчас соединяем с автором внешним ключом:
    author_id = Column(Integer, ForeignKey("author.id"), nullable = False)
    author = relationship("Author", backref="comments")
    post_id = Column(Integer, ForeignKey("post.id"), nullable = False)
    post = relationship("Post", backref = "comments")
    parent_comment_id = Column(Integer, ForeignKey("comments.id"), nullable = True)

class Tag(Base, IdMixin, UrlMixin, NameMixin):
    __tablename__ = 'tag'
    posts = relationship("Post", secondary = posts_tags)



