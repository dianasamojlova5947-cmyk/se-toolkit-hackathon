"""Keyboards package for Matrix Bot."""

from .reply import (
    build_main_keyboard,
    build_admin_keyboard,
    build_language_keyboard,
    build_admin_fasting_keyboard
)
from .inline import (
    build_week_keyboard,
    build_ingredients_keyboard,
    build_fasting_keyboard,
    build_dish_select_keyboard,
    build_confirm_keyboard,
    build_edit_fields_keyboard
)

__all__ = [
    # Reply keyboards
    "build_main_keyboard",
    "build_admin_keyboard",
    "build_language_keyboard",
    "build_admin_fasting_keyboard",
    # Inline keyboards
    "build_week_keyboard",
    "build_ingredients_keyboard",
    "build_fasting_keyboard",
    "build_dish_select_keyboard",
    "build_confirm_keyboard",
    "build_edit_fields_keyboard",
]