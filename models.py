from sqlalchemy import create_engine, update
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



engine = create_engine('sqlite:///app.db?check_same_thread=False', echo=False, pool_recycle=7200)

Session = sessionmaker(bind=engine)
Base = declarative_base()
Session.configure(bind=engine)
session = Session()

class Words(Base):
    __tablename__ = 'Words'
    word = Column(String, primary_key=True)

class Group_ids(Base):
    __tablename__ = 'Group_ids'
    group_id = Column(Integer, primary_key=True)

class Users_ids(Base):
    __tablename__ = 'Users_ids'
    user_id = Column(Integer, primary_key=True)

class Buffer_buttons(Base):
    __tablename__ = 'Buffer_buttons'
    button = Column(String, primary_key=True)
    script_part = Column(String)

class Buffer_values(Base):
    __tablename__ = 'Buffer_values'
    value = Column(String, primary_key=True)
    script_part = Column(String)

class Page_number(Base):
    __tablename__ = 'Page_number'
    page_number = Column(Integer, primary_key=True)

# class Admin(Base):
#     __tablename__ = 'Admin'
#     id = Column(Integer, primary_key=True)

class Cache(Base):
    __tablename__ = 'Cache'
    id = Column(Integer, primary_key=True, autoincrement=True)
    target_id = Column(Integer)
    post_id = Column(Integer)
    item_id = Column(Integer)


class Parser_DB():

    def clear_cache(self):
        session.query(Cache).delete()
        session.commit()

    def add_cache(self, target_id, post_id, item_id):
        session.add(Cache(target_id=target_id, post_id=post_id, item_id=item_id))
        session.commit()

    def fetch_cache(self, target_id, post_id, item_id):
        result = session.query(Cache).filter(Cache.target_id == target_id,
                                    Cache.post_id == post_id, Cache.item_id == item_id).first()
        if result:
            return (result.target_id, result.post_id, result.item_id)

    # def set_admin_id(self, id):
    #     session.add(Admin(id=id))
    #     session.commit()

class Admin_panel_db():
    def clear_buffer(self):
        session.query(Buffer_values).delete()
        session.query(Buffer_buttons).delete()
        session.commit()

    def fetch_page_number(self):
        result = session.query(Page_number).first()
        return result.page_number

    def set_page_number(self, page_number: int):
        session.execute(update(Page_number).values(page_number=page_number))
        session.commit()

    def fetch_all_groups(self):
        results = session.query(Group_ids).all()
        return [result.group_id for result in results]

    def fetch_all_users_ids(self):
        results = session.query(Users_ids).all()
        return [result.user_id for result in results]

    def add_user_id(self, user_id: int):
        session.add(Users_ids(user_id=user_id))
        session.commit()

    def fetch_all_words(self):
        results = session.query(Words).all()
        return [result.word for result in results]

    def fetch_buttons(self, script_part):
        results = session.query(Buffer_buttons).filter(Buffer_buttons.script_part == script_part).all()
        return [result.button for result in results]

    def fetch_values(self, script_part):
        results = session.query(Buffer_values).filter(Buffer_values.script_part == script_part).all()
        return [result.value for result in results]

    def getGroupIds(self):
        results = session.query(Group_ids).all()
        return [result.group_id for result in results]

    def delete_word(self, word: str):
        session.query(Words).filter(Words.word == word).delete()
        session.commit()

    def deleta_group_id(self, group_id: int):
        session.query(Group_ids).filter(Group_ids.group_id == group_id).delete()
        session.commit()

    def delete_user_id(self, user_id: int):
        session.query(Users_ids).filter(Users_ids.user_id == user_id).delete()
        session.commit()

    def save_button(self, payload: str, script_part: str):
        session.add(Buffer_buttons(button=payload, script_part=script_part))
        session.commit()

    def save_value(self, value: str, script_part: str):
        session.add(Buffer_values(value=value, script_part=script_part))
        session.commit()

metadata = Base.metadata
