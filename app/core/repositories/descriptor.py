from typing import Generic, Type, TypeVar, overload, Any

from app.core.repositories.base import AbstractRepository


Repo = TypeVar('Repo', bound=AbstractRepository)


class LazyRepo(Generic[Repo]):
    """Descriptor for lazy repository initialization."""

    def __init__(self, repo_class: Type[Repo]):
        self.repo_class = repo_class
        self.attr_name: str | None = None

    def __set_name__(self, owner: Type[Repo], name: str) -> None:
        """Called when descriptor is assigned to class attribute."""
        self.attr_name = f'_{name}'

    @overload
    def __get__(self, obj: None, objtype: type) -> "LazyRepo[Repo]": ...

    @overload
    def __get__(self, obj: Any, objtype: type | None = None) -> Repo: ...

    def __get__(
        self,
        obj: Any | None,
        objtype: type | None = None
    ) -> "LazyRepo[Repo] | Repo":
        """Get repository, creating it lazily if needed."""
        if obj is None:
            return self

        if self.attr_name is None:
            raise RuntimeError(
                "LazyRepo descriptor was not properly initialized. "
                "__set_name__ was not called."
            )

        repo: Repo | None = getattr(obj, self.attr_name, None)

        if repo is None:
            repo = self.repo_class(obj.uow)
            setattr(obj, self.attr_name, repo)

        return repo
