from pypdf import PdfReader
from datetime import date
import re
import uuid
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship
from sqlalchemy.dialects.postgresql import UUID

class Base(DeclarativeBase):
    pass

class Councilour(Base):
    __tablename__ = "councilours"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(sqlalchemy.String, nullable=False)
    phone: Mapped[str] = mapped_column(sqlalchemy.String, nullable=False)
    email: Mapped[str] = mapped_column(sqlalchemy.String, nullable=False)
    photo_url: Mapped[str] = mapped_column(sqlalchemy.String, nullable=False)
    party: Mapped[str] = mapped_column(sqlalchemy.String, nullable=False)

    attendances: Mapped[list["Attendence"]] = relationship(back_populates="councilour")

class Attendence(Base):
    __tablename__ = "attendences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    councilor_id: Mapped[uuid.UUID] = mapped_column(sqlalchemy.ForeignKey("councilours.id"), nullable=False)
    month: Mapped[date] = mapped_column(default=date.today)
    status: Mapped[str] = mapped_column(nullable=False)

    councilour: Mapped["Councilour"] = relationship(back_populates="attendances")


def get_attendence_status_from_scrapped_str(text: str):
    return re.search(r"\b(PRESENTE|Ausente|Justificado)\b", text, re.IGNORECASE).group()

def get_name_from_scrapped_str(text: str):
    return re.sub(r"\b(PRESENTE|Ausente|Justificado)\b", "", text, re.IGNORECASE).strip()

def add_attendence(attendences: list[Attendence], text: list[str], last_month: str):
    session_date_regex = r"\d{2} de [A-Z][a-z]+ de \d{4}"
    session_date: str

    for i in text:
        if re.match(session_date_regex, i): # will always hit this condition on the first iteration
            session_date = i
            continue
        if any(x in i for x in ['PRESENTE', 'Ausente', 'Justificado']):
            attendences.append(Attendence(status=get_attendence_status_from_scrapped_str(i)))
            continue

def throw_exception_if_current_month_already_executed(client: sqlalchemy.Engine):
    with Session(client) as session:
        stmt = sqlalchemy.select(Attendence)
        results = session.scalars(stmt).all()

        for a in results:
            print(f"ID: {a.id}, Councilor ID: {a.councilor_id}, Month: {a.month}, Status: {a.status}")

client = sqlalchemy.create_engine(
    "postgresql+psycopg2://postgres:postgres@localhost:5432/paoecirco.org",
    echo=True
)

Base.metadata.create_all(client)

throw_exception_if_current_month_already_executed(client)

today = date.today()
last_month = f"{today.year}/{today.month - 1}/{today.day}" 
print(f"\nIniciando a raspagem do relatório de presenças em {last_month}.\n")

path = "t.pdf" ## TODO get from environment variable

reader = PdfReader(path)
page = reader.pages[0]
text = page.extract_text().splitlines()

attendences = []

for i in range(len(reader.pages)):
    page = reader.pages[i]
    text = page.extract_text().splitlines()
    add_attendence(attendences, text, last_month)