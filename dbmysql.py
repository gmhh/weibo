from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref


engine = create_engine("mysql+pymysql://weibo:123456@localhost/weibodb?charset=utf8", pool_size=100)
Base = declarative_base(engine)


class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True)
    password = Column(String(64))
    weibo_user = relationship("WeiboUser", backref="admin")


class WeiboUser(Base):
    __tablename__ = 'weibo_user'

    weibo_id = Column(String(64), primary_key=True) # 这里是微博的uid
    weibo_username = Column(String(64), unique=True)
    weibo_password = Column(String(64))
    weibo_nickname = Column(String(64))
    weibo_count = Column(Integer)
    user_id = Column(String(64), ForeignKey("user.username"))
    log = relationship("ForwardLog", backref="weibo_user")
    follow = relationship("WeiboFollow", backref="weibo_user")
    weibodom = relationship("WeiboDom", backref="weibo_user")


class ForwardLog(Base):
    __tablename__ = 'forward_log'

    id = Column(Integer, primary_key=True)
    forwarded_user_id = Column(String(64))
    forwarded_username = Column(String(64))
    content_summary = Column(Text)
    weibo_user_id = Column(String(64), ForeignKey("weibo_user.weibo_id"))
    forward_time = Column(DateTime)


class WeiboFollow(Base):
    __tablename__ = 'weibo_follow'

    id = Column(Integer, primary_key=True)
    followed_weibo_id = Column(String(64))  # 这里是被关注者的微博id
    followed_weibo_name = Column(String(64))
    weibo_user_id = Column(String(64), ForeignKey("weibo_user.weibo_id"))
    is_used = Column(Integer)  # 是否被用于转发


class WeiboDom(Base):
    __tablename__ = "weibo_dom"

    id = Column(Integer, primary_key=True)
    this_weibo_user_id = Column(String(64))
    weibo_username = Column(String(64))
    weibo_content_id = Column(String(64))
    weibo_content = Column(Text)
    mid = Column(String(64))
    weibo_user_id = Column(String(64), ForeignKey("weibo_user.weibo_id"))  # 这里的userid是转发账号的uid，不是这条微博所有者的uid
    is_forward = Column(Integer)


class OneWord(Base):
    __tablename__ = "one_word"

    id = Column(Integer, primary_key=True)
    hitokoto = Column(Text)
    word_type = Column(String(4))
    word_from = Column(String(32))
    creator = Column(String(32))
    created_at = Column(String(64))
    

class Food(Base):
    __tablename__ = "food"

    id = Column(Integer, primary_key=True)
    title = Column(String(128))
    material = Column(Text)
    food_img = Column(String(128))
    food_url = Column(String(128))
    is_used = Column(Integer)


if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
