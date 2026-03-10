import time
from app import celery_app


def send_bbok_notification(book_id, title):
    print(f"Starting notification task for book {book_id}:{title}")
