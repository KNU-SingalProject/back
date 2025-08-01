from sqlalchemy import Column, Integer, String, Enum, Date, TIMESTAMP, text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    gender = Column(Enum("male", "female", name="gender_type"), nullable=False)
    birth = Column(Date, nullable=False)
    age = Column(int, nullable=False)
    phone_num = Column(String(128), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class Facility(Base):
    __tablename__ = "facility"

    id = Column(Integer, primary_key=True, index = True)
    facility_name = Column(String(30), nullable=False)

class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, index = True)
    title = Column(String(128), nullable=False)
    content = Column(text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    board_id = relationship("BoardImage", back_populates="board", cascade="all, delete-orphan")

class BoardImage(Base):
    __tablename__ = "board_image"

    id = Column(Integer, primary_key=True, index = True)
    board_id = Column(Integer, nullable=False)
    image_url = Column(text, nullable=False)


class MemberFacility(Base):
    __tablename__ = "member_facility"

    user_id = Column(Integer, primary_key=True, index = True, nullable=False)
    facility_id = Column(Integer, primary_key=True, index = True, nullable=False)
    usage_date = Column(Date, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class FacilityStatus(Base):
    __tablename__ = "facility_status"

    id = Column(Integer, primary_key=True, index = True)
    facility_id = Column(Integer, nullable=False)
    status = Column(Enum("active", "inactive", "off", name="facility_status"), nullable=False)

class MemberVisit(Base):
    __tablename__ = "member_visit"

    id = Column(Integer, primary_key=True, index = True)
    user_id = Column(Integer, nullable=False)
    visit_time = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class FacilityReservation(Base):
    __tablename__ = "facility_reservation"

    id = Column(Integer, primary_key=True, index = True)
    facility_id = Column(Integer, nullable=False)
    status = Column(Enum("available", "wait", name="reservation_status"), default="available", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

class ReservationUser(Base):
    __tablename__ = "reservation_user"

    id = Column(Integer, primary_key=True, index = True)
    reservation_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)