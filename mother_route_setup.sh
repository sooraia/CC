echo "1 rt_eth0" >> /etc/iproute2/rt_tables
echo "2 rt_eth1" >> /etc/iproute2/rt_tables
echo "3 rt_eth2" >> /etc/iproute2/rt_tables

# rotas para as tabelas
ip route add 10.0.1.0/24 dev eth0 src 10.0.1.20 table rt_eth0
ip route add default via 10.0.1.1 table rt_eth0

ip route add 10.0.10.0/24 dev eth1 src 10.0.10.20 table rt_eth1
ip route add default via 10.0.10.1 table rt_eth1

ip route add 10.0.12.0/24 dev eth2 src 10.0.12.20 table rt_eth2
ip route add default via 10.0.12.1 table rt_eth2

# regras por origem
ip rule add from 10.0.1.20/32 table rt_eth0
ip rule add from 10.0.10.20/32 table rt_eth1
ip rule add from 10.0.12.20/32 table rt_eth2