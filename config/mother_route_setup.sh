echo "1 rt_eth0" >> /etc/iproute2/rt_tables
echo "2 rt_eth1" >> /etc/iproute2/rt_tables
echo "3 rt_eth2" >> /etc/iproute2/rt_tables

# tabela da if eth0
ip route add 10.0.1.0/24 dev eth0 src 10.0.1.20 table rt_eth0
ip route add default via 10.0.1.1 dev eth0 table rt_eth0

# tabela da if eth1
ip route add 10.0.10.0/24 dev eth1 src 10.0.10.20 table rt_eth1
ip route add default via 10.0.10.1 dev eth1 table rt_eth1

# tabela da if eth2
ip route add 10.0.12.0/24 dev eth2 src 10.0.12.20 table rt_eth2
ip route add default via 10.0.12.1 dev eth2 src 10.0.12.20 table rt_eth2

# regras para cada subnet
ip rule add to 10.0.0.0/24 table rt_eth0 
ip rule add to 10.0.8.0/24 table rt_eth1 #subnet do 03
ip rule add to 10.0.9.0/24 table rt_eth1 #subnet do 04
ip rule add to 10.0.11.0/24 table rt_eth2 #subnet do ground

