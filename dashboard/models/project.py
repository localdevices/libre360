from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy_serializer import SerializerMixin
from models.base import Base


class Project(Base, SerializerMixin):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    n_cams = Column(Integer, nullable=False)
    dt = Column(Integer, nullable=False)

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
