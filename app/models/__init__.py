"""SQLAlchemy ``Base`` and ORM models registered on ``Base.metadata``.

Import ``Base`` from this package so model modules load (side effects) and tables
register on ``Base.metadata``. Feature models must use
``from app.models.base import Base`` so this ``__init__`` does not import names
from those modules (that would re-enter a half-loaded ``items.model``).
"""

from .base import Base

import app.modules.items.model  # pyright: ignore[reportUnusedImport]
import app.modules.users.model  # pyright: ignore[reportUnusedImport]

__all__ = ["Base"]
