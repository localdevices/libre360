import uuid
from sqlalchemy import Integer, ForeignKey, String, DateTime, Column
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_serializer import SerializerMixin
from models.base import Base


class Photo(Base, SerializerMixin):
    __tablename__ = "photo"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=False)
    survey_id = Column(Integer, ForeignKey("survey.id"), nullable=False)
    hostname = Column(String, nullable=False)
    file = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    def __str__(self):
        return "{}".format(self.name)

    def __repr__(self):
        return "{}: {}".format(self.id, self.__str__())
