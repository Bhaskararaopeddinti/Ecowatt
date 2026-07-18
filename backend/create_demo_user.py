from database import init_db, SessionLocal
from models import User
from utils.auth import get_password_hash

init_db()
db = SessionLocal()
existing = db.query(User).filter(User.username == 'demo').first()
if not existing:
    user = User(
        username='demo',
        email='demo@example.com',
        hashed_password=get_password_hash('Bhanu@777'),
        full_name='Demo User',
        phone='0000000000',
        address='Demo Address',
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print('created', user.id)
else:
    print('exists', existing.id)
db.close()
