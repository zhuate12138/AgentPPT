"""PPT-related data models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class CreateMode(str, Enum):
    """PPT creation mode."""
    NO_TEMPLATE = "no_template"
    WITH_TEMPLATE = "with_template"


class EditInstructionType(str, Enum):
    """Types of edit instructions."""
    SET_TEXT = "set_text"
    SET_TITLE = "set_title"
    SET_BODY = "set_body"
    ADD_BULLET = "add_bullet"
    SET_BULLETS = "set_bullets"
    DELETE_SHAPE = "delete_shape"
    ADD_TEXT_BOX = "add_text_box"


class EditInstruction(BaseModel):
    """A single edit instruction."""
    type: EditInstructionType
    slide_index: int = Field(..., ge=0, description="0-based slide index")
    shape_id: Optional[str] = Field(None, description="Shape identifier or placeholder name")
    content: Optional[str] = Field(None, description="New content text")
    bullets: Optional[List[str]] = Field(None, description="List items for set_bullets")
    position: Optional[dict] = Field(None, description="Position for new shapes {left, top, width, height}")


class SlideSummary(BaseModel):
    """Summary of a single slide for context."""
    index: int
    title: Optional[str] = None
    body_text: Optional[str] = None
    has_image: bool = False
    has_chart: bool = False
    notes: Optional[str] = None
    shape_count: int = 0


class PPTSummary(BaseModel):
    """Summary of entire PPT for LLM context."""
    total_slides: int
    slides: List[SlideSummary]
    theme: Optional[str] = None


class SlideDetail(BaseModel):
    """Detailed content of a slide."""
    index: int
    shapes: List[dict] = Field(default_factory=list, description="List of shapes with their content")


class ProjectMeta(BaseModel):
    """Project metadata."""
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    current_version: int = 1
    total_versions: int = 1
    topic: Optional[str] = None


class VersionMeta(BaseModel):
    """Version metadata."""
    version: int
    created_at: datetime
    description: Optional[str] = None
    is_confirmed: bool = True


# Request/Response models

class CreatePPTRequest(BaseModel):
    """Request to create a new PPT."""
    topic: str = Field(..., min_length=1, max_length=500)
    mode: CreateMode = CreateMode.NO_TEMPLATE
    template_id: Optional[str] = None
    additional_context: Optional[str] = None


class CreatePPTResponse(BaseModel):
    """Response after creating a PPT."""
    project_id: str
    version: int
    slide_count: int
    summary: PPTSummary


class EditPPTRequest(BaseModel):
    """Request to edit a PPT."""
    project_id: str
    version: int
    prompt: str = Field(..., min_length=1, max_length=2000)
    current_slide_index: Optional[int] = Field(None, ge=0)


class EditPPTResponse(BaseModel):
    """Response after editing a PPT."""
    project_id: str
    old_version: int
    new_version: int
    is_confirmed: bool = False
    instructions_executed: List[EditInstruction]
    preview_images: List[str] = Field(default_factory=list, description="URLs to preview images")


class ConfirmEditRequest(BaseModel):
    """Request to confirm an edit."""
    project_id: str
    version: int


class CancelEditRequest(BaseModel):
    """Request to cancel an edit."""
    project_id: str
    version: int


class GetProjectResponse(BaseModel):
    """Response for project details."""
    meta: ProjectMeta
    versions: List[VersionMeta]
    current_summary: PPTSummary


class GetSlidesResponse(BaseModel):
    """Response for slide preview images."""
    project_id: str
    version: int
    slides: List[dict] = Field(default_factory=list, description="[{index, image_url}]")


class UploadMaterialRequest(BaseModel):
    """Request metadata for material upload."""
    project_id: str
    material_type: str = Field("document", pattern="^(document|template)$")


class MaterialInfo(BaseModel):
    """Information about uploaded material."""
    id: str
    filename: str
    material_type: str
    size_bytes: int
    uploaded_at: datetime


class RestoreVersionRequest(BaseModel):
    """Request to restore to a specific version."""
    project_id: str
    target_version: int