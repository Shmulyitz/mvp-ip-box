from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rtsp_main_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    rtsp_sub_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_stream: Mapped[str] = mapped_column(String(10), default="sub")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cells: Mapped[list["LayoutCell"]] = relationship(back_populates="camera")


class Layout(Base):
    __tablename__ = "layouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    grid_size: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cells: Mapped[list["LayoutCell"]] = relationship(back_populates="layout", cascade="all, delete-orphan")


class LayoutCell(Base):
    __tablename__ = "layout_cells"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    layout_id: Mapped[int] = mapped_column(ForeignKey("layouts.id"), nullable=False)
    cell_index: Mapped[int] = mapped_column(Integer, nullable=False)
    camera_id: Mapped[int | None] = mapped_column(ForeignKey("cameras.id"), nullable=True)
    stream_type: Mapped[str] = mapped_column(String(10), default="sub")

    layout: Mapped[Layout] = relationship(back_populates="cells")
    camera: Mapped[Camera | None] = relationship(back_populates="cells")


class StreamStatus(Base):
    __tablename__ = "stream_status"

    camera_id: Mapped[int] = mapped_column(ForeignKey("cameras.id"), primary_key=True)
    status: Mapped[str] = mapped_column(String(64), default="unknown")
    last_frame_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    reconnect_count: Mapped[int] = mapped_column(Integer, default=0)
    fps: Mapped[float | None] = mapped_column(Float, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level: Mapped[str] = mapped_column(String(32), default="info")
    event_type: Mapped[str] = mapped_column(String(64), default="system")
    camera_id: Mapped[int | None] = mapped_column(ForeignKey("cameras.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")
