from app import Card, db
from faker import Faker

fake = Faker()


db.drop_all()
db.create_all()

cards = [
    Card(uid=fake.random_number(fix_len=True, digits=8), name=fake.street_name())
    for _ in range(10)
]
db.session.add_all(cards)
db.session.commit()
db.session.close()
