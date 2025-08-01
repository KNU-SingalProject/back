from sqlalchemy import Column, Integer, String, Enum, Date, TIMESTAMP, text, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import date

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    member_id = Column(Integer, primary_key=True)  # 재단에서 부여한 6자리 숫자
    name = Column(String(50), nullable=False)
    gender = Column(Enum("male", "female", name="gender_type"), nullable=False)
    birth = Column(Date, nullable=False)
    age = Column(Integer, nullable=False)
    phone_num = Column(String(128), nullable=False, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relationships
    visits = relationship("MemberVisit", back_populates="user", cascade="all, delete-orphan")
    facilities = relationship("MemberFacility", back_populates="user", cascade="all, delete-orphan")
    reservations = relationship("ReservationUser", back_populates="user", cascade="all, delete-orphan")

    @classmethod
    def create(cls, member_id: str, name: str, birth: date, gender: str, hashed_phone_num: str) -> "User":
        today = date.today()
        age = today.year - birth.year
        if (today.month, today.day) < (birth.month, birth.day):
            age -= 1

        return cls(
            member_id=member_id,
            name=name,
            gender=gender,
            birth=birth,
            age=age,
            phone_num=hashed_phone_num
        )

class Facility(Base):
    __tablename__ = "facility"

    id = Column(Integer, primary_key=True, index=True)
    facility_name = Column(String(30), nullable=False)

    # Relationships
    statuses = relationship("FacilityStatus", back_populates="facility", cascade="all, delete-orphan")
    reservations = relationship("FacilityReservation", back_populates="facility", cascade="all, delete-orphan")
    member_facilities = relationship("MemberFacility", back_populates="facility", cascade="all, delete-orphan")


class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    images = relationship("BoardImage", back_populates="board", cascade="all, delete-orphan")


class BoardImage(Base):
    __tablename__ = "board_image"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("board.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)

    board = relationship("Board", back_populates="images")


class MemberFacility(Base):
    __tablename__ = "member_facility"

    user_id = Column(Integer, ForeignKey("users.member_id", ondelete="CASCADE"), primary_key=True, index=True, nullable=False)
    facility_id = Column(Integer, ForeignKey("facility.id", ondelete="CASCADE"), primary_key=True, index=True, nullable=False)
    usage_date = Column(Date, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    user = relationship("User", back_populates="facilities")
    facility = relationship("Facility", back_populates="member_facilities")


class FacilityStatus(Base):
    __tablename__ = "facility_status"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facility.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("active", "inactive", "off", name="facility_status"), nullable=False)

    facility = relationship("Facility", back_populates="statuses")


class MemberVisit(Base):
    __tablename__ = "member_visit"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.member_id", ondelete="CASCADE"), nullable=False)
    visit_time = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    user = relationship("User", back_populates="visits")


class FacilityReservation(Base):
    __tablename__ = "facility_reservation"

    id = Column(Integer, primary_key=True, index=True)
    facility_id = Column(Integer, ForeignKey("facility.id", ondelete="CASCADE"), nullable=False)
    status = Column(Enum("available", "wait", name="reservation_status"), server_default="available", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    facility = relationship("Facility", back_populates="reservations")
    reservation_users = relationship("ReservationUser", back_populates="reservation", cascade="all, delete-orphan")


class ReservationUser(Base):
    __tablename__ = "reservation_user"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("facility_reservation.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.member_id", ondelete="CASCADE"), nullable=False)

    reservation = relationship("FacilityReservation", back_populates="reservation_users")
    user = relationship("User", back_populates="reservations")
