from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from models.base import Base

# TODO: Remove hardcoded connection URI.
engine = create_engine("postgresql://libre360:zanzibar@localhost:5432/libre360", pool_size=50, max_overflow=0)

from models import project
from models import survey
from models import user
from models import device
from models import photo

# TODO: Persistent database by removing drop all once DB models are stable..
# Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
db = scoped_session(DBSession)
Base.query = db.query_property()
