from django.apps import AppConfig


def _ensure_locales():
    try:
        from home.utils.i18n import ensure_compiled_catalogs

        ensure_compiled_catalogs()
    except Exception:
        # Import-time errors should never prevent the application from starting.
        # The logging happens inside the helper; silent fallback here keeps
        # migrations and collectstatic running in constrained environments.
        pass


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self) -> None:  # pragma: no cover - exercised during startup
        _ensure_locales()
        super().ready()
