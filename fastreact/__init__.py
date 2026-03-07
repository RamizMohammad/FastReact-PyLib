from .core import FastReact

__version__ = "0.1.0"
__all__ = ["FastReact", "FlaskReact"]


def __getattr__(name):
    """
    Lazy import FlaskReact only when explicitly requested.
    This prevents Flask import errors for users who only use FastReact.
    """
    if name == "FlaskReact":
        from .flask_core import FlaskReact
        return FlaskReact
    raise AttributeError(f"module 'fastreact' has no attribute {name!r}")