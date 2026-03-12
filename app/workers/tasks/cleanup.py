from ..celery_app import celery_app

@celery_app.task
def cleanup_old_documents(days: int = 30):
    return {"status": "success", "deleted": 0}
