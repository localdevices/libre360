import enum
from sqlalchemy import Integer, ForeignKey, String, Column, Enum, Float, event
from sqlalchemy_serializer import SerializerMixin
from models.base import Base

class DeviceStatus(enum.Enum):
    OFFLINE = 0
    IDLE = 1
    READY = 2
    CAPTURE = 3
    STREAM = 4
    BROKEN = 9

class DeviceType(enum.Enum):
    PARENT = 0
    CHILD = 1

class Device(Base, SerializerMixin):
    __tablename__ = "device"
    id = Column(Integer, primary_key=True)  # on-the-fly created id of device
    device_type = Column(Enum(DeviceType), nullable=False)
    hostname = Column(String, nullable=False)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.IDLE)
    request_time = Column(String, nullable=False)  # last moment that device was reporting its status

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

