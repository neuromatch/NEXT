#!/bin/sh

for i in `seq 2 $CELERY_ASYNC_WORKER_COUNT`
do
    celery -A next.broker.celery_app worker -l warning --concurrency=${CELERY_THREADS_PER_ASYNC_WORKER} -n async_worker_${i}@${HOSTNAME} -Q async@${HOSTNAME} --prefetch-multiplier=${CELERY_ASYNC_WORKER_PREFETCH} &
done

for i in `seq 2 $CELERY_DASHBOARD_WORKER_COUNT`
do
    celery -A next.broker.celery_app worker -l warning --concurrency=${CELERY_THREADS_PER_DASHBOARD_WORKER} -n dashboard_worker_${i}@${HOSTNAME} -Q dashboard@${HOSTNAME} --prefetch-multiplier=${CELERY_DASHBOARD_WORKER_PREFETCH} &
done

for i in `seq 2 $CELERY_SYNC_WORKER_COUNT`
do
    celery -A next.broker.celery_app worker -l warning --concurrency=1 -n sync_worker_${i}@${HOSTNAME} -Q sync_queue_${i}@${HOSTNAME} --prefetch-multiplier=1 &
done




export i=1
celery -A next.broker.celery_app worker -l warning --concurrency=${CELERY_THREADS_PER_ASYNC_WORKER} -n async_worker_${i}@${HOSTNAME} -Q async@${HOSTNAME} --prefetch-multiplier=${CELERY_ASYNC_WORKER_PREFETCH} &
celery -A next.broker.celery_app worker -l warning --concurrency=1 -n sync_worker_${i}@${HOSTNAME} -Q sync_queue_${i}@${HOSTNAME} --prefetch-multiplier=1 &
celery -A next.broker.celery_app worker -l warning --concurrency=${CELERY_THREADS_PER_DASHBOARD_WORKER} -n dashboard_worker_${i}@${HOSTNAME} -Q dashboard@${HOSTNAME} --prefetch-multiplier=${CELERY_DASHBOARD_WORKER_PREFETCH}


# celery -A next.broker.celery_app worker -l info --loglevel=info --concurrency=1 -n async_queue_worker_$i@%h -Q global_pool,async_queue_$HOSTNAME &
# celery -A next.broker.celery_app worker -l info --loglevel=info --concurrency=$CELERY_THREADS_PER_WORKER -n sync_queue_worker_1@%h -Q global_pool,sync_queue_$HOSTNAME
