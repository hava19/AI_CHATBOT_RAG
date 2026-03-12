import structlog

logger = structlog.get_logger()

def setup_logging():
    structlog.configure(
        processors=[
            structlog.processors.JSONRenderer()
        ]
    )
