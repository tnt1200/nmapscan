import time
import datetime
import traceback
from operator import attrgetter


from celery import chain, chord, group
from celery.exceptions import MaxRetriesExceededError
from celery.utils.log import get_task_logger

from nmapscan.celery import app
from nmapscan.func.nmap import ping_scan, scan_ip
from nmapscan.db.model import TargetForScan

logger = get_task_logger(__name__)

# NmapHost.objects().distinct(field="address")

@app.task()
def sche_check_targets():
    logger.info("fetching tasks")
    for obj in TargetForScan.objects(scaned=False):
        obj.scaned = True
        obj.save()
        scan_single_ip.delay(obj,3600)


@app.task()
def scan_single_ip(targetobj,timeout):
    logger.info("Begin Scanning {} timeout = {}".format(targetobj.addr, timeout))
    try:
        targetobj.scan_start = datetime.datetime.now()
        targetobj.scanning = True
        targetobj.save()
        scan_ip(targetobj.addr, ping=False, timeout=timeout)
    except Exception as e:
        targetobj.scanning = False
        targetobj.failed = "failed"
        targetobj.save()
    else:
        targetobj.scanning = False
        targetobj.scan_end = datetime.datetime.now()
        targetobj.save()
