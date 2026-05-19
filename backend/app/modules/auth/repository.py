from app.repositories.base import BaseRepository


class AuthRepository(BaseRepository):
    """Persistence boundary for authentication workflows.

    Authentication uses user and role repositories for concrete queries; this
    class remains the module-level extension point for token/session persistence
    if refresh tokens are added later.
    """

    pass
