from threading import Thread
import json
import time
from datetime import datetime
import enum
from flask import current_app
from sqlalchemy import Integer, String, Column, DateTime, Enum, event, table, create_engine
from sqlalchemy_serializer import SerializerMixin

from models.base import Base
from models.survey import Survey
from models.gps import Gps

class DeviceStatus(enum.Enum):
    OFFLINE = 0
    IDLE = 1
    READY = 2
    CAPTURE = 3
    STREAM = 4
    BROKEN = 5

class DeviceType(enum.Enum):
    PARENT = 0
    CHILD = 1

class Device(Base, SerializerMixin):
    __tablename__ = "device"
    id = Column(Integer, primary_key=True)  # on-the-fly created id of device
    device_type = Column(Enum(DeviceType), default=DeviceType.CHILD, nullable=False)
    hostname = Column(String, nullable=False)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.IDLE)
    request_time = Column(DateTime, nullable=False)  # last moment that device was reporting its status
    def __str__(self):
        return "{}".format(self.device_type)

    def __repr__(self):
        return "{}: {} - {}".format(self.id, self.__str__(), self.status)


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
    def gps_log():
        while True:
            from models import db
            time.sleep(1)
            parent = Device.query.filter(Device.device_type == DeviceType.PARENT).first()
            print(parent.status, parent.request_time)
            if (parent.status == "CAPTURE") or (parent.status == DeviceStatus.CAPTURE):
                gpsd.gpsd_stream.write("?POLL;\n")
                gpsd.gpsd_stream.flush()
                raw = gpsd.gpsd_stream.readline()
                content = {
                    "survey_id": survey.id,
                    "request_time": datetime.strptime(json.loads(raw)["time"], "%Y-%m-%dT%H:%M:%S.%fZ"),
                    "message": json.loads(raw)["tpv"]
                }
                db.add(Gps(**content))
                db.commit()

            else:
                return

    # only switch on gps if device is a parent device and status is capture
    if ((target.status == DeviceStatus.CAPTURE) | (target.status == "CAPTURE")) & (target.device_type == DeviceType.PARENT):
        # retrieve last survey
        survey = Survey.query.order_by(Survey.id.desc()).first()
        import gpsd
        try:
            gpsd.connect()
            current_app.logger.info(f"Logging survey {survey.id} to GPS {gpsd.device()}")
            thread = Thread(target=gps_log)
            thread.start()
        except:
            current_app.logger.info(f"No GPS, so not logging GPS")

    else:
        current_app.logger.info("Stopping GPS logging")
