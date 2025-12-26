"""Pydantic models for trip sharing and collaboration."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class CollaboratorRole(str, Enum):
    """Collaborator permission levels."""

    VIEWER = "viewer"  # Can view trip and comments
    EDITOR = "editor"  # Can edit itinerary and add comments
    OWNER = "owner"  # Full access (only for trip creator)


class ShareLinkStatus(str, Enum):
    """Share link status."""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ShareLinkExpiry(str, Enum):
    """Predefined share link expiry options."""

    NEVER = "never"
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    NINETY_DAYS = "90d"


# === Share Link Models ===


class ShareSettingsBase(BaseModel):
    """Base model for share settings."""

    is_public: bool = Field(default=False, description="Whether the link is publicly accessible")
    allow_comments: bool = Field(default=True, description="Whether viewers can see comments")
    allow_copy: bool = Field(default=False, description="Whether viewers can copy the trip")
    expiry: ShareLinkExpiry = Field(default=ShareLinkExpiry.NEVER, description="Link expiry period")


class ShareSettingsCreate(ShareSettingsBase):
    """Request model for creating/updating share settings."""

    pass


class ShareSettings(ShareSettingsBase):
    """Share settings response model."""

    trip_id: str
    share_token: Optional[str] = None
    share_url: Optional[str] = None
    status: ShareLinkStatus = ShareLinkStatus.ACTIVE
    expires_at: Optional[datetime] = None
    view_count: int = 0
    last_viewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShareLinkResponse(BaseModel):
    """Response for share link generation."""

    share_token: str
    share_url: str
    expires_at: Optional[datetime] = None
    settings: ShareSettings


class PublicTripView(BaseModel):
    """Minimal trip data for public shared view."""

    id: str
    title: str
    destinations: list[dict]
    trip_details: dict
    allow_comments: bool
    allow_copy: bool
    created_at: datetime


# === Collaborator Models ===


class CollaboratorBase(BaseModel):
    """Base model for collaborator."""

    email: EmailStr
    role: CollaboratorRole = Field(default=CollaboratorRole.VIEWER)


class CollaboratorInvite(CollaboratorBase):
    """Request model for inviting a collaborator."""

    message: Optional[str] = Field(default=None, max_length=500, description="Optional invitation message")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: CollaboratorRole) -> CollaboratorRole:
        """Prevent setting role to owner - only trip creator is owner."""
        if v == CollaboratorRole.OWNER:
            raise ValueError("Cannot assign owner role to collaborators")
        return v


class CollaboratorUpdate(BaseModel):
    """Request model for updating collaborator permissions."""

    role: CollaboratorRole

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: CollaboratorRole) -> CollaboratorRole:
        """Prevent setting role to owner - only trip creator is owner."""
        if v == CollaboratorRole.OWNER:
            raise ValueError("Cannot assign owner role to collaborators")
        return v


class Collaborator(CollaboratorBase):
    """Collaborator response model."""

    id: str
    trip_id: str
    user_id: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    invited_by: str
    invited_at: datetime
    accepted_at: Optional[datetime] = None
    is_pending: bool = True

    class Config:
        from_attributes = True


class CollaboratorListResponse(BaseModel):
    """Response for listing collaborators."""

    collaborators: list[Collaborator]
    total: int
    owner: Collaborator  # Trip owner info


class InvitationResponse(BaseModel):
    """Response for collaboration invitation."""

    id: str
    email: str
    role: CollaboratorRole
    invitation_url: str
    expires_at: Optional[datetime] = None


class InvitationAcceptRequest(BaseModel):
    """Request for accepting an invitation."""

    token: str


class InvitationAcceptResponse(BaseModel):
    """Response for accepting an invitation."""

    trip_id: str
    trip_title: str
    role: CollaboratorRole
    accepted_at: datetime


# === Comment Models ===


class CommentBase(BaseModel):
    """Base model for comment."""

    content: str = Field(..., min_length=1, max_length=5000)
    section_type: Optional[str] = Field(
        default=None,
        description="Optional section the comment relates to (visa, destination, itinerary, flight)",
    )


class CommentCreate(CommentBase):
    """Request model for creating a comment."""

    parent_id: Optional[str] = Field(default=None, description="Parent comment ID for replies")


class CommentUpdate(BaseModel):
    """Request model for updating a comment."""

    content: str = Field(..., min_length=1, max_length=5000)


class CommentAuthor(BaseModel):
    """Comment author info."""

    id: str
    name: str
    avatar_url: Optional[str] = None
    is_owner: bool = False


class Comment(CommentBase):
    """Comment response model."""

    id: str
    trip_id: str
    author: CommentAuthor
    parent_id: Optional[str] = None
    is_edited: bool = False
    reply_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """Response for listing comments."""

    comments: list[Comment]
    total: int
    has_more: bool = False


class CommentThread(BaseModel):
    """Comment with replies."""

    comment: Comment
    replies: list[Comment] = []
