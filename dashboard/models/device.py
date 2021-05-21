import enum
from sqlalchemy import Integer, String, Column, Enum, event
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


@event.listens_for(Device, "after_update")
def receive_after_update(mapper, connection, target):
    """
    Check if parent has changed status to CAPTURE
    If so, check if gps device is ready and providing NMEA messages on gpsd socket
    If so, capture a coordinate every second
    If that is the case
    :param mapper:
    :param connection:
    :param target:
    """
    # FIXME: get gps running when parent is in status DeviceStatus.CAPTURE (arrange this in the model instead of
    #  here)
    print("+++++++++++++++++++++++++++++++++")
    print("IMPLEMENT GPS READER IN THIS PART")
    print("+++++++++++++++++++++++++++++++++")
    # # starting gps
    # if gpsd is not None:
    #     # log gpsd messages
    #     try:
    #         gps_kwargs = {
    #             "conn": cur.connection,
    #             "gpsd_stream": gpsd.gpsd_stream,
    #             "project_id": cur_project["project_id"],
    #             "survey_run": survey_run,
    #         }
    #         Thread(target=gps_log, kwargs=gps_kwargs).start()
    #         logger.info("Started GPS log")
    #     except:
    #         msg = "GPS connected but not responding"
            #         logger.error(msg)
