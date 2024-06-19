import os

from datetime import timedelta

## Broker settings.
broker_url = os.environ.get('CELERY_BROKER_URL')
broker_connection_retry = True
broker_channel_error_retry = True
broker_connection_retry_on_startup = True
broker_connection_max_retries = None # retry forever

# List of modules to import when the Celery worker starts.
imports = ('transactions.tasks',)

# # Using the database to store task state and results.
# result_backend = 'django-db'
# # store task name and args in database
# result_extended = True
# # default is 1 day
# result_expires = timedelta(weeks=1)

# Use Django Cache
cache_backend = 'django-cache'

# timezone
timezone = 'Asia/Tehran'

task_serializer = 'pickle'

accept_content = {'json', 'pickle'}

# worker_hijack_root_logger = False
# worker_redirect_stdouts = False
# # worker_redirect_stdouts_level = 'INFO'
# worker_max_tasks_per_child = 1
# # don't prefetch tasks as the tasks are long running
# worker_prefetch_multiplier = 1
# # handled by docker scaling system
# worker_concurrency = 1