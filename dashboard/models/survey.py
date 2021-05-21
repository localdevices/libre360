from sqlalchemy import Integer, ForeignKey, String, Column, DateTime
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship

from models.base import Base


class Survey(Base, SerializerMixin):
    __tablename__ = "survey"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    project_id = Column(Integer, ForeignKey("project.id"))
    project = relationship("Project", cascade="all, delete")

    def __str__(self):
        return "{} in {}".format(self.id, self.project.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())

