import os
import json

class BaseGenerator:
    """Provides common filesystem and JSON schema parsing utilities."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def build(self):
        """Must be implemented by child classes."""
        raise NotImplementedError("Subclasses must implement build() method.")
