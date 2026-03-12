from ..celery_app import celery_app

@celery_app.task
def batch_embedding(doc_ids: list):
    return {"status": "success", "processed": len(doc_ids)}
