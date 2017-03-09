from celery import Celery, platforms

app = Celery()
app.config_from_object('nmapscan.celery_config')
platforms.C_FORCE_ROOT = True


if __name__ == "__main__":
    app.start()
