#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.cli import CLI


class part1_topo(Topo):
    def build(self):
        s1 = self.addSwitch("s1")
        for i in range(1,5):
            hostname = "h{index}".format(index=i)
            mac_addr = "00:00:00:00:00:0{index}".format(index=i)
            ip_addr = "10.0.0.{index}/24".format(index=i)
            host = self.addHost(hostname, mac=mac_addr, ip=ip_addr)
            self.addLink(host, s1)
        
        topology = """
        [h1]-----{s1}------[h2]
        [h3]----/    \-----[h4]
        """

        print("Creating network topology")
        print(topology)

topos = {"part1": part1_topo}

if __name__ == "__main__":
    t = part1_topo()
    net = Mininet(topo=t)
    net.start()
    CLI(net)
    net.stop()