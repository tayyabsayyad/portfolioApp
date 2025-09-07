# trades/utils.py
from .models import ActivityLog


def log_activity(user, action, target=None, details=None):
    """
    Create an ActivityLog entry.
    - user: User object or None
    - action: short string summary e.g. "Added trade"
    - target: optional model instance (will store model name and pk)
    - details: optional text
    """
    target_type = None
    target_id = None
    if target is not None:
        try:
            target_type = target.__class__.__name__
            target_id = getattr(target, 'id', str(target))
        except Exception:
            target_type = str(type(target))
            target_id = str(target)

    ActivityLog.objects.create(
        user=getattr(user, 'pk', None) and user or None,
        action=action[:200],
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        details=(details or '')[:2000]
    )
