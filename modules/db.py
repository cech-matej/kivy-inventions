from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy.types import String, Integer, Enum, Text, BLOB, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

SQLITE = 'sqlite'
MYSQL = 'mysql'

Base = declarative_base()


# InventionCategory = Table('inventioncategory', Base.metadata,
#                           Column('invention_id', Integer, ForeignKey('inventions.id')),
#                           Column('category_id', Integer, ForeignKey('categories.id')))

class InventionCategory(Base):
    __tablename__ = 'inventioncategory'

    invention_id = Column(Integer, ForeignKey('inventions.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)


class Inventor(Base):
    __tablename__ = 'inventors'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthday = Column(Date)
    date_of_death = Column(Date)
    nation_id = Column(Integer, ForeignKey('nations.id'), nullable=False)
    inventions = relationship('Invention', backref='inventor_backref')
    # invention = Column(Integer, ForeignKey('inventions.id'))
    biography = Column(Text)
    photo = Column(BLOB)


class Nation(Base):
    __tablename__ = 'nations'

    id = Column(Integer, primary_key=True)
    abbr = Column(String(5), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    flag = Column(BLOB)
    form_of_state = Column(Enum('Monarchy', 'Republic', 'Theocracy'))
    inventors = relationship('Inventor', backref='nation_backref')


class Invention(Base):
    __tablename__ = 'inventions'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    inventor = Column(Integer, ForeignKey('inventors.id'))
    # inventors = relationship('Inventor', backref='invention2')
    description = Column(Text)
    date_of_invention = Column(Date)
    '''category = Column(Integer, ForeignKey('categories.id'))'''
    category = relationship('Category', secondary='inventioncategory', backref='invention')
    photo = Column(BLOB)


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    '''inventions = relationship('Invention', backref='category2')'''
    '''inventions = relationship('Invention', secondary=InventionCategory, backref='category2')'''


class Database:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}',
        MYSQL: 'mysql+mysqlconnector://{USERNAME}:{PASSWORD}@localhost/{DB}'
    }

    def __init__(self, dbtype='sqlite', username='', password='', dbname='../inventions.db'):
        dbtype = dbtype.lower()

        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname, USERNAME=username, PASSWORD=password)
            self.engine = create_engine(engine_url, echo=False)
        else:
            print('DBType is not found in DB_ENGINE')

        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_invention(self, invention):
        try:
            self.session.add(invention)
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def create_nation(self, nation):
        try:
            self.session.add(nation)
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def create_inventor(self, inventor):
        try:
            self.session.add(inventor)
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def create_category(self, category):
        try:
            self.session.add(category)
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_inventions(self, order=Invention.name):
        try:
            result = self.session.query(Invention).order_by(order).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_invention_by_id(self, idx):
        try:
            result = self.session.query(Invention).get(idx)
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_inventions_by_category(self, category):
        try:
            # result = self.session.query(Invention).join(Category).filter(Category.name.like(f'%{category}%'))\
            #     .order_by(Invention.name).all()
            result = self.session.query(Invention).join(InventionCategory).join(Category)\
                .filter(Category.name.like(f'%{category}%')).filter(InventionCategory.category_id == Category.id)\
                .order_by(Invention.name).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_inventions_by_nation(self, nation):
        try:
            result = self.session.query(Invention).join(Inventor).join(Nation).filter(Nation.abbr.like(f'%{nation}%')) \
                .order_by(Invention.name).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_inventors(self, order=Inventor.last_name):
        try:
            result = self.session.query(Inventor).order_by(order).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_inventor_by_id(self, idx):
        try:
            result = self.session.query(Inventor).get(idx)
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_inventors_by_category(self, category):
        try:
            # result = self.session.query(Inventor).join(Invention).join(Category)\
            #     .filter(Category.name.like(f'%{category}%'))\
            #     .order_by(Inventor.last_name).all()
            result = self.session.query(Inventor).join(Invention).join(InventionCategory).join(Category) \
                .filter(Category.name.like(f'%{category}%')).filter(InventionCategory.category_id == Category.id) \
                .order_by(Inventor.last_name).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_inventors_by_nation(self, nation):
        try:
            result = self.session.query(Inventor).join(Nation).filter(Nation.abbr.like(f'%{nation}%'))\
                .order_by(Inventor.last_name).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_nations(self, order=Nation.name):
        try:
            result = self.session.query(Nation).order_by(order).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_nation_by_id(self, idx):
        try:
            result = self.session.query(Nation).get(idx)
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_nations_by_category(self, category):
        try:
            # result = self.session.query(Nation).join(Inventor).join(Invention)\
            #     .join(Category).filter(Category.name.like(f'%{category}%'))\
            #     .order_by(Nation.name).all()
            result = self.session.query(Nation).join(Inventor).join(Invention).join(InventionCategory).join(Category) \
                .filter(Category.name.like(f'%{category}%')).filter(InventionCategory.category_id == Category.id) \
                .order_by(Nation.name).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_categories(self, order=Category.name):
        try:
            result = self.session.query(Category).order_by(order).all()
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def read_category_by_id(self, idx):
        try:
            result = self.session.query(Category).get(idx)
            return result
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def update(self):
        try:
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def delete_invention(self, idx):
        try:
            invention = self.read_invention_by_id(idx)
            self.session.delete(invention)
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def delete_inventor(self, idx):
        try:
            inventor = self.read_inventor_by_id(idx)
            self.session.delete(inventor)
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def delete_nation(self, idx):
        try:
            nation = self.read_nation_by_id(idx)
            self.session.delete(nation)
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False

    def delete_category(self, idx):
        try:
            category = self.read_category_by_id(idx)
            self.session.delete(category)
            self.session.commit()
            return True
        except Exception as e:
            print(e.__traceback__.tb_frame)
            return False
