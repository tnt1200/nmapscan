import datetime

from mongoengine import *

from nmapscan.settings import *

connect(db=MONGO_DB, host=MONGO_HOST, port=MONGO_PORT, connect=False)


class TargetForScan(Document):
    addr = StringField()
    created_at = DateTimeField(default=datetime.datetime.now)
    scan_start = DateTimeField()
    scan_end = DateTimeField()
    scanning = BooleanField(default=False)
    scaned = BooleanField(default=False)
    failed = StringField()


class NmapService(EmbeddedDocument):
    banner = StringField()
    id = StringField()
    port = StringField()
    protocol = StringField()
    reason = StringField()
    service = StringField()
    state = StringField()  # open


class NmapHost(Document):
    address = StringField()
    hostnames = StringField()
    status = StringField()  # up
    open_ports = ListField(EmbeddedDocumentField(NmapService))
    created_at = DateTimeField(default=datetime.datetime.now)
