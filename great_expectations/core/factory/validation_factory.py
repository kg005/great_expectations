from __future__ import annotations

from typing import TYPE_CHECKING, cast

from great_expectations._docs_decorators import public_api
from great_expectations.analytics.client import submit as submit_event
from great_expectations.analytics.events import (
    ValidationConfigCreatedEvent,
    ValidationConfigDeletedEvent,
)
from great_expectations.compatibility.typing_extensions import override
from great_expectations.core.factory.factory import Factory
from great_expectations.core.validation_config import ValidationConfig
from great_expectations.exceptions.exceptions import DataContextError

if TYPE_CHECKING:
    from great_expectations.data_context.store.validation_config_store import (
        ValidationConfigStore,
    )


class ValidationFactory(Factory[ValidationConfig]):
    def __init__(self, store: ValidationConfigStore) -> None:
        self._store = store

    @public_api
    @override
    def add(self, validation: ValidationConfig) -> ValidationConfig:
        """Add a ValidationConfig to the collection.

        Parameters:
            validation: ValidationConfig to add

        Raises:
            DataContextError if ValidationConfig already exists
        """
        key = self._store.get_key(name=validation.name, id=None)
        if self._store.has_key(key=key):
            raise DataContextError(
                f"Cannot add ValidationConfig with name {validation.name} because it already exists."
            )
        self._store.add(key=key, value=validation)

        submit_event(
            event=ValidationConfigCreatedEvent(
                validation_config_id=validation.id,
                expectation_suite_id=validation.expectation_suite.id,
                batch_config_id=validation.data.id,
            )
        )

        return validation

    @public_api
    @override
    def delete(self, validation: ValidationConfig) -> ValidationConfig:
        """Delete a ValidationConfig from the collection.

        Parameters:
            validation: ValidationConfig to delete

        Raises:
            DataContextError if ValidationConfig doesn't exist
        """
        key = self._store.get_key(name=validation.name, id=validation.id)
        if not self._store.has_key(key=key):
            raise DataContextError(
                f"Cannot delete ValidationConfig with name {validation.name} because it cannot be found."
            )
        self._store.remove_key(key=key)

        submit_event(
            event=ValidationConfigDeletedEvent(
                validation_config_id=validation.id,
                expectation_suite_id=validation.expectation_suite.id,
                batch_config_id=validation.data.id,
            )
        )

        return validation

    @public_api
    @override
    def get(self, name: str) -> ValidationConfig:
        """Get a ValidationConfig from the collection by name.

        Parameters:
            name: Name of ValidationConfig to get

        Raises:
            DataContextError when ValidationConfig is not found.
        """
        key = self._store.get_key(name=name, id=None)
        if not self._store.has_key(key=key):
            raise DataContextError(f"ValidationConfig with name {name} was not found.")

        return cast(ValidationConfig, self._store.get(key=key))
