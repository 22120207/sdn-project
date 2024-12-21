#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI


class part1_topo(Topo):
    def build(self):
        s1 = self.addSwitch("s1")
        for i in range(1,5):
            hostname = f"h{i}"
            mac_addr = f"00:00:00:00:00:0{i}"
            ip_addr = "10.0.0.{i{/24"
            host = self.addHost(host, mac=mac_addr, ip=ip_addr)
            
            self.addLink(host, s1)

topos = {"part1": part1_topo}

if __name__ == "__main__":
    t = part1_topo()
    net = Mininet(topo=t, controller=None)
    net.start()
    CLI(net)
    net.stop()
