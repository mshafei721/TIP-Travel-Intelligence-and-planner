"""
Trip Sharing and Collaboration API Endpoints.

Provides endpoints for:
- Share link generation and management
- Collaborator invitations and permissions
- Comment CRUD operations
- Public/shared trip access
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.auth import verify_jwt_token
from app.core.config import settings
from app.core.supabase import get_supabase_client
from app.models.sharing import (
    Collaborator,
    CollaboratorInvite,
    CollaboratorListResponse,
    CollaboratorRole,
    CollaboratorUpdate,
    Comment,
    CommentAuthor,
    CommentCreate,
    CommentListResponse,
    CommentUpdate,
    InvitationAcceptRequest,
    InvitationAcceptResponse,
    InvitationResponse,
    PublicTripView,
    ShareLinkExpiry,
    ShareLinkResponse,
    ShareLinkStatus,
    ShareSettings,
    ShareSettingsCreate,
)

router = APIRouter(tags=["sharing"])


# ============================================================================
# Utility Functions
# ============================================================================


def generate_share_token() -> str:
    """Generate a unique share token."""
    return secrets.token_urlsafe(32)


def calculate_expiry(expiry: ShareLinkExpiry) -> Optional[datetime]:
    """Calculate expiry datetime from expiry enum."""
    if expiry == ShareLinkExpiry.NEVER:
        return None
    elif expiry == ShareLinkExpiry.SEVEN_DAYS:
        return datetime.utcnow() + timedelta(days=7)
    elif expiry == ShareLinkExpiry.THIRTY_DAYS:
        return datetime.utcnow() + timedelta(days=30)
    elif expiry == ShareLinkExpiry.NINETY_DAYS:
        return datetime.utcnow() + timedelta(days=90)
    return None


async def verify_trip_ownership(trip_id: str, user_id: str) -> dict:
    """Verify user owns the trip. Returns trip data or raises 403/404."""
    supabase = get_supabase_client()
    result = supabase.table("trips").select("*").eq("id", trip_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Trip not found")

    if result.data.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this trip")

    return result.data


async def can_access_trip(trip_id: str, user_id: str) -> tuple[bool, str]:
    """Check if user can access trip (owner or collaborator). Returns (can_access, role)."""
    supabase = get_supabase_client()

    # Check ownership
    trip = supabase.table("trips").select("user_id").eq("id", trip_id).single().execute()
    if trip.data and trip.data.get("user_id") == user_id:
        return True, "owner"

    # Check collaboration
    collab = (
        supabase.table("trip_collaborators")
        .select("role, accepted_at")
        .eq("trip_id", trip_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if collab.data and collab.data.get("accepted_at"):
        return True, collab.data.get("role")

    return False, ""


# ============================================================================
# Share Link Endpoints
# ============================================================================


@router.post("/trips/{trip_id}/share", status_code=status.HTTP_201_CREATED)
async def generate_share_link(
    trip_id: str,
    settings: ShareSettingsCreate,
    token_payload: dict = Depends(verify_jwt_token),
) -> ShareLinkResponse:
    """Generate a new share link for a trip."""
    user_id = token_payload.get("user_id")
    trip = await verify_trip_ownership(trip_id, user_id)

    supabase = get_supabase_client()

    # Generate unique token
    share_token = generate_share_token()
    expires_at = calculate_expiry(settings.expiry)

    # Create or update share link
    share_data = {
        "trip_id": trip_id,
        "created_by": user_id,
        "share_token": share_token,
        "status": ShareLinkStatus.ACTIVE.value,
        "is_public": settings.is_public,
        "allow_comments": settings.allow_comments,
        "allow_copy": settings.allow_copy,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }

    result = supabase.table("share_links").insert(share_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create share link")

    share_link = result.data
    base_url = settings.FRONTEND_URL

    return ShareLinkResponse(
        share_token=share_token,
        share_url=f"{base_url}/shared/{share_token}",
        expires_at=expires_at,
        settings=ShareSettings(
            trip_id=trip_id,
            share_token=share_token,
            share_url=f"{base_url}/shared/{share_token}",
            is_public=settings.is_public,
            allow_comments=settings.allow_comments,
            allow_copy=settings.allow_copy,
            expires_at=expires_at,
            status=ShareLinkStatus.ACTIVE,
            view_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ),
    )


@router.get("/trips/{trip_id}/share")
async def get_share_settings(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
) -> ShareSettings:
    """Get share settings for a trip."""
    user_id = token_payload.get("user_id")
    trip = await verify_trip_ownership(trip_id, user_id)

    supabase = get_supabase_client()
    result = (
        supabase.table("share_links")
        .select("*")
        .eq("trip_id", trip_id)
        .eq("status", "active")
        .single()
        .execute()
    )

    if not result.data:
        # Return default settings (no share link)
        return ShareSettings(
            trip_id=trip_id,
            is_public=False,
            allow_comments=True,
            allow_copy=False,
            expiry=ShareLinkExpiry.NEVER,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    link = result.data
    base_url = settings.FRONTEND_URL

    return ShareSettings(
        trip_id=trip_id,
        share_token=link.get("share_token"),
        share_url=f"{base_url}/shared/{link.get('share_token')}",
        is_public=link.get("is_public", False),
        allow_comments=link.get("allow_comments", True),
        allow_copy=link.get("allow_copy", False),
        status=ShareLinkStatus(link.get("status", "active")),
        expires_at=datetime.fromisoformat(link["expires_at"]) if link.get("expires_at") else None,
        view_count=link.get("view_count", 0),
        last_viewed_at=(
            datetime.fromisoformat(link["last_viewed_at"]) if link.get("last_viewed_at") else None
        ),
        created_at=datetime.fromisoformat(link["created_at"]),
        updated_at=datetime.fromisoformat(link["updated_at"]),
    )


@router.put("/trips/{trip_id}/share")
async def update_share_settings(
    trip_id: str,
    settings: ShareSettingsCreate,
    token_payload: dict = Depends(verify_jwt_token),
) -> ShareSettings:
    """Update share settings for a trip."""
    user_id = token_payload.get("user_id")
    await verify_trip_ownership(trip_id, user_id)

    supabase = get_supabase_client()
    expires_at = calculate_expiry(settings.expiry)

    update_data = {
        "is_public": settings.is_public,
        "allow_comments": settings.allow_comments,
        "allow_copy": settings.allow_copy,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }

    result = (
        supabase.table("share_links")
        .update(update_data)
        .eq("trip_id", trip_id)
        .eq("status", "active")
        .execute()
    )

    return await get_share_settings(trip_id, user)


@router.delete("/trips/{trip_id}/share")
async def revoke_share_link(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
) -> dict:
    """Revoke the share link for a trip."""
    user_id = token_payload.get("user_id")
    await verify_trip_ownership(trip_id, user_id)

    supabase = get_supabase_client()
    result = (
        supabase.table("share_links")
        .update({"status": ShareLinkStatus.REVOKED.value})
        .eq("trip_id", trip_id)
        .eq("status", "active")
        .execute()
    )

    return {"message": "Share link revoked successfully"}


# ============================================================================
# Public Shared View Endpoint
# ============================================================================


@router.get("/shared/{token}")
async def view_shared_trip(token: str) -> PublicTripView:
    """View a trip via share token (public access)."""
    supabase = get_supabase_client()

    # Find share link
    link_result = (
        supabase.table("share_links").select("*").eq("share_token", token).single().execute()
    )

    if not link_result.data:
        raise HTTPException(status_code=404, detail="Shared trip not found")

    link = link_result.data

    # Check status and expiry
    if link.get("status") != "active":
        raise HTTPException(status_code=410, detail="Share link has been revoked")

    if link.get("expires_at"):
        expires_at = datetime.fromisoformat(link["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.utcnow().replace(tzinfo=expires_at.tzinfo):
            raise HTTPException(status_code=410, detail="Share link has expired")

    # Get trip data
    trip_result = (
        supabase.table("trips").select("*").eq("id", link["trip_id"]).single().execute()
    )

    if not trip_result.data:
        raise HTTPException(status_code=404, detail="Trip not found")

    trip = trip_result.data

    # Increment view count
    supabase.table("share_links").update(
        {"view_count": link.get("view_count", 0) + 1, "last_viewed_at": datetime.utcnow().isoformat()}
    ).eq("id", link["id"]).execute()

    return PublicTripView(
        id=trip["id"],
        title=trip["title"],
        destinations=trip.get("destinations", []),
        trip_details=trip.get("trip_details", {}),
        allow_comments=link.get("allow_comments", True),
        allow_copy=link.get("allow_copy", False),
        created_at=datetime.fromisoformat(trip["created_at"]),
    )


# ============================================================================
# Collaborator Endpoints
# ============================================================================


@router.post("/trips/{trip_id}/collaborators", status_code=status.HTTP_201_CREATED)
async def invite_collaborator(
    trip_id: str,
    invite: CollaboratorInvite,
    token_payload: dict = Depends(verify_jwt_token),
) -> InvitationResponse:
    """Invite a collaborator to a trip."""
    user_id = token_payload.get("user_id")
    trip = await verify_trip_ownership(trip_id, user_id)

    supabase = get_supabase_client()

    # Check if inviting self
    owner_email = trip.get("traveler_details", {}).get("email")
    if owner_email and invite.email.lower() == owner_email.lower():
        raise HTTPException(status_code=400, detail="Cannot invite yourself")

    # Check for duplicate invitation
    existing = (
        supabase.table("trip_collaborators")
        .select("id")
        .eq("trip_id", trip_id)
        .eq("email", invite.email.lower())
        .single()
        .execute()
    )

    if existing.data:
        raise HTTPException(status_code=409, detail="User already invited")

    # Generate invitation token
    invitation_token = generate_share_token()

    collab_data = {
        "trip_id": trip_id,
        "email": invite.email.lower(),
        "role": invite.role.value,
        "invited_by": user_id,
        "invitation_token": invitation_token,
    }

    result = supabase.table("trip_collaborators").insert(collab_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create invitation")

    base_url = settings.FRONTEND_URL

    return InvitationResponse(
        id=result.data["id"],
        email=invite.email,
        role=invite.role,
        invitation_url=f"{base_url}/invitations/{invitation_token}",
        expires_at=None,  # Invitations don't expire
    )


@router.get("/trips/{trip_id}/collaborators")
async def list_collaborators(
    trip_id: str,
    token_payload: dict = Depends(verify_jwt_token),
) -> CollaboratorListResponse:
    """List all collaborators for a trip."""
    user_id = token_payload.get("user_id")
    can_access, role = await can_access_trip(trip_id, user_id)

    if not can_access:
        raise HTTPException(status_code=403, detail="Not authorized to access this trip")

    supabase = get_supabase_client()

    # Get trip for owner info
    trip = supabase.table("trips").select("user_id, traveler_details").eq("id", trip_id).single().execute()

    # Get collaborators
    result = supabase.table("trip_collaborators").select("*").eq("trip_id", trip_id).execute()

    collaborators = []
    for collab in result.data or []:
        collaborators.append(
            Collaborator(
                id=collab["id"],
                trip_id=trip_id,
                user_id=collab.get("user_id"),
                email=collab["email"],
                role=CollaboratorRole(collab["role"]),
                invited_by=collab["invited_by"],
                invited_at=datetime.fromisoformat(collab["created_at"]),
                accepted_at=(
                    datetime.fromisoformat(collab["accepted_at"]) if collab.get("accepted_at") else None
                ),
                is_pending=collab.get("accepted_at") is None,
            )
        )

    # Create owner entry
    traveler = trip.data.get("traveler_details", {})
    owner = Collaborator(
        id=trip.data["user_id"],
        trip_id=trip_id,
        user_id=trip.data["user_id"],
        email=traveler.get("email", ""),
        name=traveler.get("name"),
        role=CollaboratorRole.OWNER,
        invited_by=trip.data["user_id"],
        invited_at=datetime.utcnow(),
        accepted_at=datetime.utcnow(),
        is_pending=False,
    )

    return CollaboratorListResponse(
        collaborators=collaborators,
        total=len(collaborators),
        owner=owner,
    )


@router.put("/trips/{trip_id}/collaborators/{collab_user_id}")
async def update_collaborator(
    trip_id: str,
    collab_user_id: str,
    update: CollaboratorUpdate,
    token_payload: dict = Depends(verify_jwt_token),
) -> Collaborator:
    """Update collaborator permissions."""
    user_id = token_payload.get("user_id")
    await verify_trip_ownership(trip_id, user_id)

    supabase = get_supabase_client()

    result = (
        supabase.table("trip_collaborators")
        .update({"role": update.role.value})
        .eq("trip_id", trip_id)
        .eq("user_id", collab_user_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Collaborator not found")

    collab = result.data[0] if isinstance(result.data, list) else result.data

    return Collaborator(
        id=collab["id"],
        trip_id=trip_id,
        user_id=collab.get("user_id"),
        email=collab["email"],
        role=CollaboratorRole(collab["role"]),
        invited_by=collab["invited_by"],
        invited_at=datetime.fromisoformat(collab["created_at"]),
        accepted_at=(
            datetime.fromisoformat(collab["accepted_at"]) if collab.get("accepted_at") else None
        ),
        is_pending=collab.get("accepted_at") is None,
    )


@router.delete("/trips/{trip_id}/collaborators/{collab_user_id}")
async def remove_collaborator(
    trip_id: str,
    collab_user_id: str,
    token_payload: dict = Depends(verify_jwt_token),
) -> dict:
    """Remove a collaborator from a trip."""
    user_id = token_payload.get("user_id")
    await verify_trip_ownership(trip_id, user_id)

    supabase = get_supabase_client()

    result = (
        supabase.table("trip_collaborators")
        .delete()
        .eq("trip_id", trip_id)
        .eq("user_id", collab_user_id)
        .execute()
    )

    return {"message": "Collaborator removed successfully"}


@router.post("/invitations/accept")
async def accept_invitation(
    request: InvitationAcceptRequest,
    token_payload: dict = Depends(verify_jwt_token),
) -> InvitationAcceptResponse:
    """Accept a collaboration invitation."""
    user_id = token_payload.get("user_id")
    supabase = get_supabase_client()

    # Find invitation
    invite_result = (
        supabase.table("trip_collaborators")
        .select("*, trips(title)")
        .eq("invitation_token", request.token)
        .single()
        .execute()
    )

    if not invite_result.data:
        raise HTTPException(status_code=404, detail="Invitation not found")

    invitation = invite_result.data

    # Already accepted?
    if invitation.get("accepted_at"):
        raise HTTPException(status_code=400, detail="Invitation already accepted")

    # Update invitation with user_id and accepted_at
    now = datetime.utcnow()
    update_result = (
        supabase.table("trip_collaborators")
        .update(
            {
                "user_id": user_id,
                "accepted_at": now.isoformat(),
                "invitation_token": None,  # Clear token after use
            }
        )
        .eq("id", invitation["id"])
        .execute()
    )

    # Get trip title
    trip = supabase.table("trips").select("title").eq("id", invitation["trip_id"]).single().execute()

    return InvitationAcceptResponse(
        trip_id=invitation["trip_id"],
        trip_title=trip.data.get("title", "") if trip.data else "",
        role=CollaboratorRole(invitation["role"]),
        accepted_at=now,
    )


# ============================================================================
# Comment Endpoints
# ============================================================================


@router.post("/trips/{trip_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    trip_id: str,
    comment: CommentCreate,
    token_payload: dict = Depends(verify_jwt_token),
) -> Comment:
    """Create a comment on a trip."""
    user_id = token_payload.get("user_id")
    can_access, role = await can_access_trip(trip_id, user_id)

    if not can_access:
        raise HTTPException(status_code=403, detail="Not authorized to comment on this trip")

    supabase = get_supabase_client()

    # Validate parent comment if provided
    if comment.parent_id:
        parent = (
            supabase.table("trip_comments")
            .select("id")
            .eq("id", comment.parent_id)
            .eq("trip_id", trip_id)
            .single()
            .execute()
        )
        if not parent.data:
            raise HTTPException(status_code=404, detail="Parent comment not found")

    comment_data = {
        "trip_id": trip_id,
        "user_id": user_id,
        "content": comment.content,
        "section_type": comment.section_type,
        "parent_id": comment.parent_id,
    }

    result = supabase.table("trip_comments").insert(comment_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to create comment")

    # Get user info for author
    user_profile = supabase.table("user_profiles").select("display_name, avatar_url").eq("id", user_id).single().execute()

    return Comment(
        id=result.data["id"],
        trip_id=trip_id,
        content=comment.content,
        section_type=comment.section_type,
        parent_id=comment.parent_id,
        author=CommentAuthor(
            id=user_id,
            name=user_profile.data.get("display_name", "User") if user_profile.data else "User",
            avatar_url=user_profile.data.get("avatar_url") if user_profile.data else None,
            is_owner=role == "owner",
        ),
        is_edited=False,
        reply_count=0,
        created_at=datetime.fromisoformat(result.data["created_at"]),
        updated_at=datetime.fromisoformat(result.data["updated_at"]),
    )


@router.get("/trips/{trip_id}/comments")
async def list_comments(
    trip_id: str,
    section: Optional[str] = Query(None, description="Filter by section type"),
    token_payload: dict = Depends(verify_jwt_token),
) -> CommentListResponse:
    """List comments for a trip."""
    user_id = token_payload.get("user_id")
    can_access, _ = await can_access_trip(trip_id, user_id)

    if not can_access:
        raise HTTPException(status_code=403, detail="Not authorized to view comments")

    supabase = get_supabase_client()

    # Build query
    query = supabase.table("trip_comments").select("*").eq("trip_id", trip_id)

    if section:
        query = query.eq("section_type", section)

    result = query.order("created_at", desc=False).execute()

    # Get trip owner for is_owner flag
    trip = supabase.table("trips").select("user_id").eq("id", trip_id).single().execute()
    trip_owner_id = trip.data.get("user_id") if trip.data else None

    comments = []
    for c in result.data or []:
        # Get author info
        author_profile = (
            supabase.table("user_profiles")
            .select("display_name, avatar_url")
            .eq("id", c["user_id"])
            .single()
            .execute()
        )

        # Count replies
        reply_count = (
            supabase.table("trip_comments")
            .select("id", count="exact")
            .eq("parent_id", c["id"])
            .execute()
        )

        comments.append(
            Comment(
                id=c["id"],
                trip_id=trip_id,
                content=c["content"],
                section_type=c.get("section_type"),
                parent_id=c.get("parent_id"),
                author=CommentAuthor(
                    id=c["user_id"],
                    name=(
                        author_profile.data.get("display_name", "User")
                        if author_profile.data
                        else "User"
                    ),
                    avatar_url=author_profile.data.get("avatar_url") if author_profile.data else None,
                    is_owner=c["user_id"] == trip_owner_id,
                ),
                is_edited=c.get("is_edited", False),
                reply_count=reply_count.count or 0,
                created_at=datetime.fromisoformat(c["created_at"]),
                updated_at=datetime.fromisoformat(c["updated_at"]),
            )
        )

    return CommentListResponse(
        comments=comments,
        total=len(comments),
        has_more=False,
    )


@router.put("/trips/{trip_id}/comments/{comment_id}")
async def update_comment(
    trip_id: str,
    comment_id: str,
    update: CommentUpdate,
    token_payload: dict = Depends(verify_jwt_token),
) -> Comment:
    """Update a comment."""
    user_id = token_payload.get("user_id")

    supabase = get_supabase_client()

    # Get the comment
    comment_result = (
        supabase.table("trip_comments").select("*").eq("id", comment_id).single().execute()
    )

    if not comment_result.data:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment = comment_result.data

    # Verify ownership
    if comment["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    # Update
    result = (
        supabase.table("trip_comments")
        .update({"content": update.content, "is_edited": True})
        .eq("id", comment_id)
        .execute()
    )

    updated = result.data[0] if isinstance(result.data, list) else result.data

    # Get author info
    author_profile = (
        supabase.table("user_profiles")
        .select("display_name, avatar_url")
        .eq("id", user_id)
        .single()
        .execute()
    )

    # Get trip owner
    trip = supabase.table("trips").select("user_id").eq("id", trip_id).single().execute()

    return Comment(
        id=updated["id"],
        trip_id=trip_id,
        content=updated["content"],
        section_type=updated.get("section_type"),
        parent_id=updated.get("parent_id"),
        author=CommentAuthor(
            id=user_id,
            name=author_profile.data.get("display_name", "User") if author_profile.data else "User",
            avatar_url=author_profile.data.get("avatar_url") if author_profile.data else None,
            is_owner=user_id == trip.data.get("user_id") if trip.data else False,
        ),
        is_edited=True,
        reply_count=0,
        created_at=datetime.fromisoformat(updated["created_at"]),
        updated_at=datetime.fromisoformat(updated["updated_at"]),
    )


@router.delete("/trips/{trip_id}/comments/{comment_id}")
async def delete_comment(
    trip_id: str,
    comment_id: str,
    token_payload: dict = Depends(verify_jwt_token),
) -> dict:
    """Delete a comment."""
    user_id = token_payload.get("user_id")

    supabase = get_supabase_client()

    # Get trip to check ownership
    trip = supabase.table("trips").select("user_id").eq("id", trip_id).single().execute()

    # Get comment
    comment = supabase.table("trip_comments").select("user_id").eq("id", comment_id).single().execute()

    if not comment.data:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check authorization: comment author or trip owner
    is_comment_author = comment.data["user_id"] == user_id
    is_trip_owner = trip.data and trip.data["user_id"] == user_id

    if not is_comment_author and not is_trip_owner:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    # Delete
    supabase.table("trip_comments").delete().eq("id", comment_id).execute()

    return {"message": "Comment deleted successfully"}
