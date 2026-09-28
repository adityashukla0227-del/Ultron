"""
Ultron Capability
Version: v0.93

Defines the core capability contract for Ultron.

Responsibilities:
- Define capability identity
- Store capability description
- Store capability metadata
- Validate capability configuration

Capability registration belongs to CapabilityRegistry.
Capability authorization belongs to the security/permission layer.
Capability execution belongs to existing AgentTool / AgentEngine layers.
"""

from typing import Any, Dict, Optional


class CapabilityValidationError(Exception):
    """Raised when a capability configuration is invalid."""


class Capability:
    """
    Core representation of an Ultron capability.

    A Capability describes a discrete ability that one or more
    AgentTool objects may provide.

    Capability does not execute tools.
    Capability does not grant permissions.
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        self.name = (
            name.strip()
            if isinstance(name, str)
            else name
        )

        self.description = (
            description.strip()
            if isinstance(description, str)
            else description
        )

        if metadata is None:
            self.metadata = {}
        elif isinstance(metadata, dict):
            self.metadata = dict(metadata)
        else:
            raise CapabilityValidationError(
                "Capability metadata must be a dictionary."
            )

        self.validate()

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate the complete capability configuration.
        """

        if not isinstance(
            self.name,
            str,
        ):
            raise CapabilityValidationError(
                "Capability name must be a string."
            )

        if not self.name.strip():
            raise CapabilityValidationError(
                "Capability name is required."
            )

        if not isinstance(
            self.description,
            str,
        ):
            raise CapabilityValidationError(
                "Capability description must be a string."
            )

        if not isinstance(
            self.metadata,
            dict,
        ):
            raise CapabilityValidationError(
                "Capability metadata must be a dictionary."
            )

        return True

    # ========================================================
    # Metadata Management
    # ========================================================

    def set_metadata(
        self,
        metadata: Optional[Dict[str, Any]],
    ) -> None:
        """
        Replace capability metadata.
        """

        if metadata is None:
            metadata = {}

        if not isinstance(
            metadata,
            dict,
        ):
            raise CapabilityValidationError(
                "Capability metadata must be a dictionary."
            )

        self.metadata = dict(metadata)

    def update_metadata(
        self,
        metadata: Dict[str, Any],
    ) -> None:
        """
        Update capability metadata.
        """

        if not isinstance(
            metadata,
            dict,
        ):
            raise CapabilityValidationError(
                "Capability metadata must be a dictionary."
            )

        self.metadata.update(metadata)

    def get_metadata(self) -> Dict[str, Any]:
        """
        Return a defensive copy of capability metadata.
        """

        return dict(self.metadata)

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert capability configuration into a dictionary.
        """

        return {
            "name": self.name,
            "description": self.description,
            "metadata": dict(
                self.metadata
            ),
        }

    # ========================================================
    # Restoration
    # ========================================================

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
    ) -> "Capability":
        """
        Restore a Capability from persistent data.
        """

        if not isinstance(
            data,
            dict,
        ):
            raise CapabilityValidationError(
                "Capability data must be a dictionary."
            )

        return cls(
            name=data.get(
                "name",
                "",
            ),
            description=data.get(
                "description",
                "",
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )

    # ========================================================
    # Representation
    # ========================================================

    def __repr__(self) -> str:
        """
        Return a developer-friendly representation.
        """

        return (
            f"Capability("
            f"name='{self.name}', "
            f"description='{self.description}'"
            f")"
        )