import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa
from sqlalchemy import JSON


POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5431)

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"


engine = create_async_engine(PG_DSN)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class SwapiPeople(Base):
    __tablename__ = "swapi_people"

    id: Mapped[int] = mapped_column(primary_key=True)
    birth_year: Mapped[str] = mapped_column()
    eye_color: Mapped[str] = mapped_column()
    films: Mapped[list] = mapped_column(JSON)
    gender: Mapped[str] = mapped_column()
    hair_color: Mapped[str] = mapped_column()
    height: Mapped[str] = mapped_column()
    homeworld: Mapped[str] = mapped_column()
    mass: Mapped[str] = mapped_column()
    name: Mapped[str] = mapped_column()
    skin_color: Mapped[str] = mapped_column()
    species: Mapped[list] = mapped_column(JSON)
    starships: Mapped[list] = mapped_column(JSON)
    url: Mapped[str] = mapped_column()
    vehicles: Mapped[list] = mapped_column(JSON)
    created: Mapped[str] = mapped_column()
    edited: Mapped[str] = mapped_column()
    url: Mapped[str] = mapped_column()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
