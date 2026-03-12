from ..celery_app import celery_app

@celery_app.task(bind=True, max_retries=3)
def process_document(self, doc_id: str):
    try:
        # Process document
        return {"status": "success", "doc_id": doc_id}
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
