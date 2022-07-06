from celery import Celery

celery_app = Celery(
    include=['changeAnalyzerSD.git_repository_mining_util'],
)
