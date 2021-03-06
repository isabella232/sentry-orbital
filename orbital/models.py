from __future__ import absolute_import

import socket

from sentry.signals import event_accepted
from sentry.utils.geo import geo_by_addr
from sentry.utils.json import dumps

from time import time

from .constants import ORBITAL_UDP_SERVER

udp_addr = ORBITAL_UDP_SERVER.split(":", 1)
udp_addr[1] = int(udp_addr[1])
udp_addr = tuple(udp_addr)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


@event_accepted.connect(weak=False)
def notify_orbital(ip, data=None, **kwargs):
    try:
        result = geo_by_addr(ip)
    except Exception:
        return

    if not result:
        return

    if data:
        platform = (data.get("platform") or "other").lower()
    else:
        platform = ""

    data = [
        round(result["latitude"], 4),
        round(result["longitude"], 4),
        int(time() * 1000),
        platform,
    ]

    udp_socket.sendto(dumps(data).encode("utf-8"), udp_addr)
