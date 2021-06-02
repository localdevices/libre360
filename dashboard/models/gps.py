from sqlalchemy import Integer, ForeignKey, String, Column, DateTime, Enum, JSON
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship

from models.base import Base

class Gps(Base, SerializerMixin):
    __tablename__ = "gps"
    id = Column(Integer, primary_key=True)  # on-the-fly created id of device
    survey_id = Column(Integer, ForeignKey("survey.id"), nullable=False)
    request_time = Column(DateTime, nullable=False)  # last moment that device was reporting its status
    message = Column(JSON, nullable=False)
    survey = relationship("Survey", cascade="all, delete")

    def __str__(self):
        return "{}".format(self.request_time)

    def __repr__(self):
        return "{}: {} - {}".format(self.id, self.__str__(), self.request_time)
