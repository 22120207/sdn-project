# Part 3 of UWCSE's Mininet-SDN project
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
import pox.lib.packet as pkt

log = core.getLogger()

# Flood all ports
all_ports = of.OFPP_FLOOD


# Convenience mappings of hostnames to ips
IPS = {
    "h10": "10.0.1.10",
    "h20": "10.0.2.20",
    "h30": "10.0.3.30",
    "serv1": "10.0.4.10",
    "hnotrust": "172.16.10.100",
}


# Convenience mappings of hostnames to subnets
SUBNETS = {
    "h10": "10.0.1.0/24",
    "h20": "10.0.2.0/24",
    "h30": "10.0.3.0/24",
    "serv1": "10.0.4.0/24",
    "hnotrust": "172.16.10.0/24",
}


PRIORITIES = {
    "highest": 100,
    "high": 80,
    "medium": 60,
    "low": 40,
    "lowest": 20,
    "no_priority": 0
}


PORT_MAPPING = {
    "h10": 1, 
    "h20": 2, 
    "h30": 3, 
    "serv1": 4, 
    "hnotrust": 5
}

class Part3Controller(object):
    """
    A Connection object for that switch is passed to the __init__ function.
    """

    def __init__(self, connection):
        print(connection.dpid)
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)

        # use the dpid to figure out what switch is being created
        if connection.dpid == 1:
            self.s1_setup()
        elif connection.dpid == 2:
            self.s2_setup()
        elif connection.dpid == 3:
            self.s3_setup()
        elif connection.dpid == 21:
            self.cores21_setup()
        elif connection.dpid == 31:
            self.dcs31_setup()
        else:
            print("UNKNOWN SWITCH")
            exit(1)
    
    def drop_packet(self, connection):
        # Drop packets that not match others flow entries
        connection.send(of.ofp_flow_mod(
            priority=PRIORITIES['no_priority']
        ))

    def allow_all_traffic(self, connection):
        # Flood to all ports
        connection.send(of.ofp_flow_mod(
            action=of.ofp_action_output(port=all_ports),
            priority=PRIORITIES['highest']
        ))

        # Drop packets that not match others flow entries
        drop_packet(connection)


    def control_icmp_traffic(self, connection):
        # NOT allow hnotrust to send ICMP REQUEST traffic
        connection.send(of.ofp_flow_mod(
            priority=PRIORITIES['highest'],
            match=of.ofp_match(dl_type=0x0800, nw_proto=pkt.ipv4.ICMP_PROTOCOL, nw_src=IPS['hnotrust'])
        ))

        # Allow authorized hosts to send icmp traffic between themselves
        for hostname, address in IPS.items():

            if hostname != "hnotrust":
                connection.send(of.ofp_flow_mod(
                    action=of.ofp_action_output(port=PORT_MAPPING[hostname]),
                    priority=PRIORITIES['high'],
                    match=of.ofp_match(dl_type=0x0800, nw_proto=pkt.ipv4.ICMP_PROTOCOL, nw_dst=address)
                ))


    def block_host_to_serv(self, connection):
        # Block a hnotrust1 IP traffic to and server
        connection.send(of.ofp_flow_mod(
            priority=PRIORITIES['medium'],
            match=of.ofp_match(dl_type=0x0800, nw_src=IPS["hnotrust"], nw_dst=IPS['serv1'])
        ))


    def allow_ip_traffic(self, connection):
        # Allow all IP traffic
        connection.send(of.ofp_flow_mod(
            action=of.ofp_action_output(port=all_ports),
            priority=PRIORITIES['low'],
            match=of.ofp_match(dl_type=0x0800)
        ))

        # Drop packets that not match others flow entries
        drop_packet(connection)
    

    ## Set up RULES ##

    def s1_setup(self):
        self.allow_all_traffic(self.connection)

    def s2_setup(self):
        self.allow_all_traffic(self.connection)

    def s3_setup(self):
        self.allow_all_traffic(self.connection)

    def cores21_setup(self):
        self.control_icmp_traffic(self.connection)
        self.block_host_to_serv(self.connection)
        self.allow_ip_traffic(self.connection)

    def dcs31_setup(self):
        self.allow_all_traffic(self.connection)

    # used in part 4 to handle individual ARP packets
    # not needed for part 3 (USE RULES!)
    # causes the switch to output packet_in on out_port
    def resend_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def _handle_PacketIn(self, event):
        """
        Packets not handled by the router rules will be
        forwarded to this method to be handled by the controller
        """

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.
        print(
            "Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump()
        )


def launch():
    """
    Starts the component
    """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Part3Controller(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)