"""
Fine-Grained Role-Based Access Control (RBAC) Module
Defines 6 Enterprise Roles:
- Admin
- RevOps
- Finance
- Operations
- Analyst
- Support

And 9 Distinct Permissions:
- READ, CREATE, UPDATE, APPROVE, EXECUTE, CONFIGURE, EXPORT, MODEL_MANAGEMENT, USER_MANAGEMENT
"""

from enum import Enum
from typing import Set, Dict, Optional
from fastapi import Header, HTTPException, Depends


class Role(str, Enum):
    ADMIN = "Admin"
    REVOPS = "RevOps"
    FINANCE = "Finance"
    OPERATIONS = "Operations"
    ANALYST = "Analyst"
    SUPPORT = "Support"


class Permission(str, Enum):
    READ = "READ"
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    APPROVE = "APPROVE"
    EXECUTE = "EXECUTE"
    CONFIGURE = "CONFIGURE"
    EXPORT = "EXPORT"
    MODEL_MANAGEMENT = "MODEL_MANAGEMENT"
    USER_MANAGEMENT = "USER_MANAGEMENT"


ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE,
        Permission.APPROVE,
        Permission.EXECUTE,
        Permission.CONFIGURE,
        Permission.EXPORT,
        Permission.MODEL_MANAGEMENT,
        Permission.USER_MANAGEMENT
    },
    Role.REVOPS: {
        Permission.READ,
        Permission.CREATE,
        Permission.UPDATE,
        Permission.APPROVE,
        Permission.EXECUTE,
        Permission.CONFIGURE,
        Permission.EXPORT,
        Permission.MODEL_MANAGEMENT
    },
    Role.FINANCE: {
        Permission.READ,
        Permission.APPROVE,
        Permission.CONFIGURE,
        Permission.EXPORT
    },
    Role.OPERATIONS: {
        Permission.READ,
        Permission.UPDATE,
        Permission.APPROVE,
        Permission.EXECUTE
    },
    Role.ANALYST: {
        Permission.READ,
        Permission.EXPORT
    },
    Role.SUPPORT: {
        Permission.READ
    }
}


def has_permission(role_str: str, required_permission: Permission) -> bool:
    """Verify whether a given role string holds the specified permission"""
    # Match role case-insensitively
    matched_role = None
    for r in Role:
        if r.value.lower() == role_str.lower():
            matched_role = r
            break

    if not matched_role:
        return False

    return required_permission in ROLE_PERMISSIONS.get(matched_role, set())


def require_permission(required_permission: Permission):
    """FastAPI Dependency Guard for RBAC Permissions"""
    async def permission_checker(x_user_role: Optional[str] = Header("Admin")):
        role = x_user_role or "Admin"
        if not has_permission(role, required_permission):
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied: Role '{role}' lacks required permission '{required_permission.value}'"
            )
        return role
    return permission_checker

