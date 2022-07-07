import threading
from typing import Callable, Generic, ParamSpec

import fastapi

import nux.models.user
import nux.models.app

P = ParamSpec('P')


class Event(Generic[P]):
    def __init__(self, name: str, f: Callable[P, None]):
        self.name = name
        self.listeners = []

    def emit(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Runs all events in separate thread"""
        for listener in self.listeners:
            listener(*args, **kwargs)

    def on(self, f: Callable[P, None]) -> Callable[P, None]:
        """Add an listener, may be used as decorator"""
        self.listeners.append(f)
        return f

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
        self.emit(*args, **kwargs)


def _user_entered_app_callback(
    user: 'nux.models.user.User',
    app: 'nux.models.app.App'
) -> None:
    """Just to setup types"""
    pass


user_entered_app = Event("user_entered_app", _user_entered_app_callback)


class NuxEvents:
    def __init__(self, background_tasks: fastapi.BackgroundTasks):
        self.background_tasks = background_tasks

    def user_entered_app(
        self,
        user: 'nux.models.user.User',
        app: 'nux.models.app.App'
    ):
        self.background_tasks.add_task(user_entered_app, user, app)


def EventsDependecy() -> NuxEvents:
    return fastapi.Depends(NuxEvents)


__all__ = (
    "Event",
    "user_entered_app",
    "NuxEvents",
    "EventsDependecy",
)
