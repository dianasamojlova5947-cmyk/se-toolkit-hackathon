"""Handlers package for Matrix Bot."""

from .start import register_start_handlers
from .menu import register_menu_handlers
from .admin import register_admin_handlers

__all__ = ["register_start_handlers", "register_menu_handlers", "register_admin_handlers"]