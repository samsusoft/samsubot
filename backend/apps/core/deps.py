# backend/apps/core/deps.py
# Dependency for getting the current user from the JWT token    
#Adding Middleware for Auth

"""Shared dependencies for routes (Auth, Tenant, DB, etc.)"""

from fastapi import Depends, Request
from apps.core.auth import get_current_user

# ------------------------------
# Auth Dependency
# ------------------------------
# Directly reuse the core auth dependency
CurrentUser = Depends(get_current_user)


# ------------------------------
# Multi-Tenant Dependency
# ------------------------------
async def get_current_tenant(request: Request) -> str:
    """
    Extract tenant_id from request.
    Strategy:
    - From headers: X-Tenant-ID
    - Or from subdomain/path (later, if needed)
    """
    tenant_id = request.headers.get("X-Tenant-ID")
    if not tenant_id:
        # You can choose to raise an exception here,
        # or fallback to a "default" tenant
        tenant_id = "default"
    return tenant_id


# ------------------------------
# Combined Dependency
# ------------------------------
async def get_user_and_tenant(
    current_user: dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant)
) -> dict:
    """Return both user and tenant info in one object"""
    return {
        "user": current_user,
        "tenant_id": tenant_id,
    }
