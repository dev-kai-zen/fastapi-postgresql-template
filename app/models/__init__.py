"""Import models from this package so they are registered on Base.metadata."""

from .base import Base

import app.modules.items.model  # pyright: ignore[reportUnusedImport]
import app.modules.users.model  # pyright: ignore[reportUnusedImport]

__all__ = ["Base"]
