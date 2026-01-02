import logging

from fastapi import APIRouter, Depends

from app.models.health import (
    DetailedHealthCheck,
    HealthCheck,
    OverallHealthStatusEnum,
    ServiceHealthStatus,
    ServiceHealthStatusEnum,
)
from app.services.openai_service import OpenAIService, get_openai_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health", response_model=HealthCheck)
async def health() -> HealthCheck:
    """
    Basic health check - always returns success if API is running.
    Use this for load balancer health checks.
    """
    return HealthCheck(status=OverallHealthStatusEnum.HEALTHY, version="1.0.0")


@router.get("/health/full", response_model=DetailedHealthCheck)
async def full_health_check(
    openai_service: OpenAIService = Depends(get_openai_service),
) -> DetailedHealthCheck:
    """
    Detailed health check including external service connectivity.
    Shows status of all dependencies.
    """
    services: dict[str, ServiceHealthStatus] = {}

    # Check OpenAI
    if openai_service.is_available:
        success, message = await openai_service.test_connection()
        services["openai"] = ServiceHealthStatus(
            status=ServiceHealthStatusEnum.CONNECTED if success else ServiceHealthStatusEnum.ERROR,
            message=message,
        )
    else:
        services["openai"] = ServiceHealthStatus(
            status=ServiceHealthStatusEnum.NOT_CONFIGURED,
            message="Service not configured",
        )

    # TODO: Add database health check when we have DB connections
    # TODO: Add Qdrant health check when vector DB is added

    # Overall status
    overall_status = OverallHealthStatusEnum.HEALTHY
    if any(s.status == ServiceHealthStatusEnum.ERROR for s in services.values()):
        overall_status = OverallHealthStatusEnum.DEGRADED

    return DetailedHealthCheck(status=overall_status, version="1.0.0", services=services)
