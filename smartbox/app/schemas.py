from datetime import datetime

from typing import Literal

from pydantic import BaseModel


class CameraBase(BaseModel):
    name: str
    ip_address: str | None = None
    rtsp_main_url: str | None = None
    rtsp_sub_url: str | None = None
    username: str | None = None
    password: str | None = None
    preferred_stream: str = "sub"
    enabled: bool = True


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: str | None = None
    ip_address: str | None = None
    rtsp_main_url: str | None = None
    rtsp_sub_url: str | None = None
    username: str | None = None
    password: str | None = None
    preferred_stream: str | None = None
    enabled: bool | None = None


class CameraOut(BaseModel):
    id: int
    name: str
    ip_address: str | None
    rtsp_main_url: str | None
    rtsp_sub_url: str | None
    username: str | None
    password: str = "***"
    preferred_stream: str
    enabled: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LayoutCellAssign(BaseModel):
    camera_id: int | None = None
    stream_type: str = "sub"


class LayoutCellOut(BaseModel):
    id: int
    layout_id: int
    cell_index: int
    camera_id: int | None
    stream_type: str

    model_config = {"from_attributes": True}


class LayoutBase(BaseModel):
    name: str
    grid_size: Literal[1, 4, 9, 16]


class LayoutCreate(LayoutBase):
    pass


class LayoutUpdate(BaseModel):
    name: str | None = None
    grid_size: int | None = None
    is_active: bool | None = None


class LayoutOut(BaseModel):
    id: int
    name: str
    grid_size: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    cells: list[LayoutCellOut] = []

    model_config = {"from_attributes": True}


class EventOut(BaseModel):
    id: int
    level: str
    event_type: str
    camera_id: int | None
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StreamStatusOut(BaseModel):
    camera_id: int
    status: str
    last_frame_at: datetime | None
    last_error: str | None
    reconnect_count: int
    fps: float | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class SettingOut(BaseModel):
    key: str
    value: str

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    api_version: str
    video_service_status: str
