from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    puntos: Mapped[int] = mapped_column(Integer, default=0)
