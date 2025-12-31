"""Pydantic models for trip sharing and collaboration."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    is_public: bool = Field(
        default=False, description="Whether the link is publicly accessible", alias="isPublic"
    )
    allow_comments: bool = Field(
        default=True, description="Whether viewers can see comments", alias="allowComments"
    )
    allow_copy: bool = Field(
        default=False, description="Whether viewers can copy the trip", alias="allowCopy"
    )
    expiry: ShareLinkExpiry = Field(default=ShareLinkExpiry.NEVER, description="Link expiry period")


class ShareSettingsCreate(ShareSettingsBase):
    """Request model for creating/updating share settings."""

    pass


class ShareSettings(ShareSettingsBase):
    """Share settings response model."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    trip_id: str = Field(..., alias="tripId")
    share_token: Optional[str] = Field(None, alias="shareToken")
    share_url: Optional[str] = Field(None, alias="shareUrl")
    status: ShareLinkStatus = ShareLinkStatus.ACTIVE
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    view_count: int = Field(default=0, alias="viewCount")
    last_viewed_at: Optional[datetime] = Field(None, alias="lastViewedAt")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")


class ShareLinkResponse(BaseModel):
    """Response for share link generation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    share_token: str = Field(..., alias="shareToken")
    share_url: str = Field(..., alias="shareUrl")
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")
    settings: ShareSettings


class PublicTripView(BaseModel):
    """Minimal trip data for public shared view."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    title: str
    destinations: list[dict]
    trip_details: dict = Field(..., alias="tripDetails")
    allow_comments: bool = Field(..., alias="allowComments")
    allow_copy: bool = Field(..., alias="allowCopy")
    created_at: datetime = Field(..., alias="createdAt")


# === Collaborator Models ===


class CollaboratorBase(BaseModel):
    """Base model for collaborator."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    email: EmailStr
    role: CollaboratorRole = Field(default=CollaboratorRole.VIEWER)


class CollaboratorInvite(CollaboratorBase):
    """Request model for inviting a collaborator."""

    message: Optional[str] = Field(
        default=None, max_length=500, description="Optional invitation message"
    )

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: CollaboratorRole) -> CollaboratorRole:
        """Prevent setting role to owner - only trip creator is owner."""
        if v == CollaboratorRole.OWNER:
            raise ValueError("Cannot assign owner role to collaborators")
        return v


class CollaboratorUpdate(BaseModel):
    """Request model for updating collaborator permissions."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

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

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    id: str
    trip_id: str = Field(..., alias="tripId")
    user_id: Optional[str] = Field(None, alias="userId")
    name: Optional[str] = None
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    invited_by: str = Field(..., alias="invitedBy")
    invited_at: datetime = Field(..., alias="invitedAt")
    accepted_at: Optional[datetime] = Field(None, alias="acceptedAt")
    is_pending: bool = Field(default=True, alias="isPending")


class CollaboratorListResponse(BaseModel):
    """Response for listing collaborators."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    collaborators: list[Collaborator]
    total: int
    owner: Collaborator  # Trip owner info


class InvitationResponse(BaseModel):
    """Response for collaboration invitation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    email: str
    role: CollaboratorRole
    invitation_url: str = Field(..., alias="invitationUrl")
    expires_at: Optional[datetime] = Field(None, alias="expiresAt")


class InvitationAcceptRequest(BaseModel):
    """Request for accepting an invitation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    token: str


class InvitationAcceptResponse(BaseModel):
    """Response for accepting an invitation."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    trip_id: str = Field(..., alias="tripId")
    trip_title: str = Field(..., alias="tripTitle")
    role: CollaboratorRole
    accepted_at: datetime = Field(..., alias="acceptedAt")


# === Comment Models ===


class CommentBase(BaseModel):
    """Base model for comment."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    content: str = Field(..., min_length=1, max_length=5000)
    section_type: Optional[str] = Field(
        default=None,
        description="Optional section the comment relates to (visa, destination, itinerary, flight)",
        alias="sectionType",
    )


class CommentCreate(CommentBase):
    """Request model for creating a comment."""

    parent_id: Optional[str] = Field(
        default=None, description="Parent comment ID for replies", alias="parentId"
    )


class CommentUpdate(BaseModel):
    """Request model for updating a comment."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    content: str = Field(..., min_length=1, max_length=5000)


class CommentAuthor(BaseModel):
    """Comment author info."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    id: str
    name: str
    avatar_url: Optional[str] = Field(None, alias="avatarUrl")
    is_owner: bool = Field(default=False, alias="isOwner")


class Comment(CommentBase):
    """Comment response model."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True, from_attributes=True)

    id: str
    trip_id: str = Field(..., alias="tripId")
    author: CommentAuthor
    parent_id: Optional[str] = Field(None, alias="parentId")
    is_edited: bool = Field(default=False, alias="isEdited")
    reply_count: int = Field(default=0, alias="replyCount")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")


class CommentListResponse(BaseModel):
    """Response for listing comments."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    comments: list[Comment]
    total: int
    has_more: bool = Field(default=False, alias="hasMore")


class CommentThread(BaseModel):
    """Comment with replies."""

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)

    comment: Comment
    replies: list[Comment] = Field(default_factory=list)
