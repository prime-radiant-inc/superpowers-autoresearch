STAFF_ROLE_PERMISSIONS = {
    "viewer": {"view"},
    "agent": {"view", "edit"},
    "supervisor": {"view", "edit", "cancel", "refund"},
    "admin": {"view", "edit", "cancel", "refund", "override"},
}


def role_can_perform(role, action):
    if role not in STAFF_ROLE_PERMISSIONS:
        raise ValueError(f"unknown staff role: {role!r}")
    return action in STAFF_ROLE_PERMISSIONS[role]
