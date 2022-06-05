# JuniperMplsStats
Junos MPLS LSP sorting and sending to influxdb with udp

Quick insight in MVPN and Transit LSPs for JUNOS(18.+) and sending them to a "local" influxdb server to visualise with Grafana for example.

Handy for troubleshooting, monitoring and just geeky stats

Runs every 5 minutes

---- PE-MVPN: Able to create graphs with:
- PE router
- LSP Name
- Source address of mcast Group
- mcast Group address
- LSP name
- LSPbytes
- LSPpackets


Assign correct variables to #bastionServer, #userName. Add PE devices to #devices array
Password is asked at run time once and can keep running after.
