"""Unit tests for common models."""

import pytest
from pydantic import ValidationError

from app.models.common import ServiceStatus, ServiceStatusEnum


def test_service_status():
    """Test ServiceStatus model."""
    status = ServiceStatus(
        status=ServiceStatusEnum.AVAILABLE,
        message="Service is working",
    )
    assert status.status == ServiceStatusEnum.AVAILABLE
    assert status.message == "Service is working"


def test_service_status_required_fields():
    """Test ServiceStatus requires both fields."""
    with pytest.raises(ValidationError):
        ServiceStatus(status="available")  # type: ignore[call-arg] # Missing message

    with pytest.raises(ValidationError):
        ServiceStatus(message="Working")  # type: ignore[call-arg] # Missing status
