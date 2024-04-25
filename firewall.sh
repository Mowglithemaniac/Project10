# Interface to block
INTERFACE="eth0"

# Flush all rules on all chains, essentially resetting the firewall
iptables -F


# Block all incoming, outgoing, and forwarded traffic on this Ethernet interface
iptables -A INPUT -i $INTERFACE -j DROP
iptables -A OUTPUT -i $INTERFACE -j DROP
iptables -A FORWARD -i $INTERFACE -j DROP
iptables -A INPUT -o $INTERFACE -j DROP
iptables -A OUTPUT -o $INTERFACE -j DROP
iptables -A FORWARD -o $INTERFACE -j DROP
