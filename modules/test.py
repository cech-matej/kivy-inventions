from modules.db import *


def read():
    print('---------------- INVENTIONS ----------------')
    print(db.read_inventions())
    print(db.read_invention_by_id(1))
    print(db.read_inventions_by_category('zdravotnictví'))
    print(db.read_inventions_by_nation('CZE'))
    print('----------------- INVENTORS ----------------')
    print(db.read_inventors())
    print(db.read_inventor_by_id(1))
    print(db.read_inventors_by_category('zdravotnictví'))
    print(db.read_inventors_by_nation('CZE'))
    print('------------------ NATIONS -----------------')
    print(db.read_nations())
    print(db.read_nation_by_id(1))
    print(db.read_nations_by_category('zdravotnictví'))
    print('---------------- CATEGORIES ----------------')
    print(db.read_categories())
    print(db.read_category_by_id(1))


db = Database(dbtype='sqlite')

nation = Nation()
nation.abbr = 'CZE'
nation.name = 'Česká republika'
db.create_nation(nation)

category = Category()
category.name = "zdravotnictví"
db.create_category(category)

inventor = Inventor()
inventor.first_name = "Otto"
inventor.last_name = "Wichterle"
inventor.nation_id = 1
inventor.invention = 1
db.create_inventor(inventor)

invention = Invention()
invention.name = 'Kontaktní čočka'
invention.inventor = 1
invention.category.append(category)
db.create_invention(invention)

invention2 = Invention()
invention2.name = 'test'
# invention2.category.append(category)
db.create_invention(invention2)


read()

db.delete_invention(1)
db.delete_inventor(1)
db.delete_nation(1)
db.delete_category(1)
print('----------------------------------------------------------------------------------------')
read()
