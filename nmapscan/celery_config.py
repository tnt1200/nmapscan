from datetime import timedelta

include = ['nmapscan.nmap_tasks']
broker_url = 'redis://:@localhost/5'
result_backend = 'redis://:@localhost/5'
worker_pool_restarts = True
result_expires = 3600
accept_content = ['pickle']
task_serializer = 'pickle'
event_serializer = 'pickle'
result_serializer = 'pickle'
beat_schedule = {
    'testadd': {
        'task': 'nmapscan.nmap_tasks.sche_check_targets',
        'schedule': timedelta(minutes=1),
        'args': ()
    }
}
