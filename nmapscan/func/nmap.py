import ipaddress
from operator import attrgetter
from datetime import datetime
from ipaddress import IPv4Network, IPv4Address
from libnmap.process import NmapProcess
from libnmap.parser import NmapParser, NmapParserException

from nmapscan.db.model import NmapHost, NmapService, TargetForScan
from nmapscan.settings import *

common_ports = '-p T:21-25,80-89,110,143,443,513,873,1080,1433,1521,1158,3306-3308,3389,3690,5900,6379,7001,8000-8090,9000,9418,27017-27019,50060,111,11211,2049'


def ping_scan(netaddr):
    """
    ping netaddr e.g. 192.168.0.0/24
    """
    baseopt = "-sn"
    nm = NmapProcess(netaddr, options="-sn")
    nm.run()
    try:
        parsed = NmapParser.parse(nm.stdout)
    except NmapParserException as e:
        print("".format(e.msg))
    else:
        return parsed


def add_scan_target(ip_or_cidr, ping=True):
    try:
        IPv4Address(ip_or_cidr)
    except ValueError as e:
        try:
            IPv4Network(ip_or_cidr)
        except ValueError as err:
            raise err
        else:
            add_netaddr(ip_or_cidr, ping=ping)
    else:
        add_ip(ip_or_cidr, ping=ping)


def add_ip(ipaddr, ping=True):
    try:
        target = IPv4Address(ipaddr)
    except ValueError as e:
        raise e
    else:
        if ping:
            parsed = ping_scan(ipaddr)
            addr = attrgetter('address')
            ips = list(
                map(addr, filter(lambda x: x.status == 'up', parsed.hosts)))
            if ips:
                now = datetime.now()
                single_ip = ips[0]
                tar = TargetForScan.objects(addr=single_ip, __raw__={
                                            'created_at': {'$gte': now - SCAN_MIN_INTERVAL}})
                if tar:
                    pass
                else:
                    TargetForScan(addr=single_ip).save()
        else:
            TargetForScan(addr=ipaddr).save()


def add_netaddr(netaddr, ping=True):
    try:
        targets = IPv4Network(netaddr)
    except ValueError as e:
        raise e
    else:
        if ping:
            parsed = ping_scan(netaddr)
            addr = attrgetter('address')
            ips = map(addr, filter(lambda x: x.status == 'up', parsed.hosts))
            now = datetime.now()
            for single_ip in ips:
                tar = TargetForScan.objects(addr=single_ip, __raw__={
                                            'created_at': {'$gte': now - SCAN_MIN_INTERVAL}})
                if tar:
                    pass
                else:
                    TargetForScan(addr=single_ip).save()
        else:
            for t in targets.hosts():
                TargetForScan(addr=str(t)).save()


def scan_ip(ipaddr, ping=True, all_port=False, timeout=3600):
    baseopt = "-sS -sV -n -T4 --open"  # syn scan
    # baseopt = "-sV -n -T4 --open" # connect scan
    if all_port:
        baseopt += ' -p-'
    else:
        baseopt + ' ' + common_ports
    if not ping:
        baseopt += " -Pn"
    if timeout:
        baseopt += " --host-timeout " + str(timeout)
    # print(baseopt)
    nm = NmapProcess(ipaddr, options=baseopt)
    nm.run()
    try:
        parsed = NmapParser.parse(nm.stdout)
    except NmapParserException as e:
        print("".format(e.msg))
    else:
        handle_parsed(parsed)


def handle_parsed(parsed):
    for host in parsed.hosts:
        handle_host_service(host)


def handle_host_service(nmap_host):
    host = NmapHost(
        address=nmap_host.address,
        hostnames=','.join(nmap_host.hostnames),
        status=nmap_host.status).save()
    for service in nmap_host.services:
        host.open_ports.append(NmapService(**service.get_dict()))
    host.save()
