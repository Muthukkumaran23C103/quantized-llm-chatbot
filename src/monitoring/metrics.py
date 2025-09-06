import time
import psutil
from typing import Dict, Any
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

MODEL_INFERENCE_COUNT = Counter(
    'model_inference_total',
    'Total number of model inferences',
    ['model_name', 'success']
)

MODEL_INFERENCE_DURATION = Histogram(
    'model_inference_duration_seconds',
    'Model inference duration in seconds',
    ['model_name']
)

CACHE_OPERATIONS = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'result']
)

DATABASE_OPERATIONS = Counter(
    'database_operations_total',
    'Total database operations',
    ['operation', 'table']
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes'
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
    
    def record_model_inference(self, model_name: str, duration: float, success: bool):
        """Record model inference metrics"""
        MODEL_INFERENCE_COUNT.labels(model_name=model_name, success=success).inc()
        if success:
            MODEL_INFERENCE_DURATION.labels(model_name=model_name).observe(duration)
    
    def record_cache_operation(self, operation: str, result: str):
        """Record cache operation metrics"""
        CACHE_OPERATIONS.labels(operation=operation, result=result).inc()
    
    def record_database_operation(self, operation: str, table: str):
        """Record database operation metrics"""
        DATABASE_OPERATIONS.labels(operation=operation, table=table).inc()
    
    def update_system_metrics(self):
        """Update system resource metrics"""
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        
        SYSTEM_MEMORY_USAGE.set(memory.used)
        SYSTEM_CPU_USAGE.set(cpu)
    
    def get_application_info(self) -> Dict[str, Any]:
        """Get application metrics summary"""
        uptime = time.time() - self.start_time
        memory = psutil.virtual_memory()
        cpu = psutil.cpu_percent()
        
        return {
            "uptime_seconds": uptime,
            "memory": {
                "used_bytes": memory.used,
                "available_bytes": memory.available,
                "percent": memory.percent
            },
            "cpu": {
                "percent": cpu,
                "count": psutil.cpu_count()
            },
            "process": {
                "pid": psutil.Process().pid,
                "memory_percent": psutil.Process().memory_percent(),
                "cpu_percent": psutil.Process().cpu_percent()
            }
        }

# Global metrics collector
metrics = MetricsCollector()

class RequestLoggingMiddleware:
    """Middleware for logging and metrics collection"""
    
    def __init__(self):
        self.logger = structlog.get_logger()
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        # Log request start
        self.logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host,
            user_agent=request.headers.get("user-agent", "")
        )
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Record metrics
            metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            # Log response
            self.logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration_ms=int(duration * 1000)
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Record error metrics
            metrics.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,
                duration=duration
            )
            
            # Log error
            self.logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                duration_ms=int(duration * 1000),
                error=str(e),
                exc_info=True
            )
            
            raise

def get_prometheus_metrics() -> str:
    """Get Prometheus-formatted metrics"""
    metrics.update_system_metrics()
    return generate_latest().decode()
