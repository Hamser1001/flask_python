import time
from app import celery_app


@celery_app.task
def send_book_notification(book_id, title):
    print(f"Starting notification task for book {book_id}:{title}")
    for x in range(20):
        time.sleep(5)
        print(x)
    print(f"Finished sending notification for book: {book_id}")
