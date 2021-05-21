import socket
from datetime import datetime
import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.device import Device
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

# remove any devices from the last session
[db.execute(table.delete()) for table in Base.metadata.sorted_tables if table.name == "device"]
db.commit()
# now add this device as parent
parent = {
    "device_type": "PARENT",
    "hostname": socket.gethostname(),
    "request_time": datetime.now(pytz.utc).strftime("%Y%m%dT%H:%M:%S.%fZ"),
    "status": "READY",
}
db.add(Device(**parent))
db.commit()
Base.query = db.query_property()
