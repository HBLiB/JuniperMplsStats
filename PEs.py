#!/usr/bin/env python3

import os
import paramiko
import getpass
import time
import traceback
import json
import socket
from datetime import datetime


data = {}
mcast = {}
mcastRaw = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

bastionServer = 'h-network.net' #Your Jump host
userName = "HBLiB"
passWord = getpass.getpass()


devices = ["PE01","PE02"]

def command(commandC,targetC):
    rawString = ""
    stdin, stdout, stderr = targetC.exec_command(commandC)
    for line in stdout.read().split(b'\n'):
        rawString = rawString + line.decode() + "\n"
    jsonC = json.loads(rawString)
    return jsonC

def connections(devices,userN,pasS):
    passWord = pasS
    bastionConnect=paramiko.SSHClient()
    bastionConnect.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    bastionConnect.connect(bastionServer, username=userN, password=passWord, port=22)
    srcIP = (bastionServer, 22)
    for device in devices:
        target=paramiko.SSHClient()
        destIP = (device, 22)
        bastionTransport = bastionConnect.get_transport()
        bastionChannel = bastionTransport.open_channel("direct-tcpip", destIP, srcIP)
        target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target.connect(destIP, username=userN, password=passWord, sock=bastionChannel)
        data[device] = command("show mpls lsp ingress statistics | display json",target)
        mcastRaw[device] = command("show mvpn c-multicast instance-name CP display-tunnel-name | display json",target)
        target.close()
        for entry2 in mcastRaw[device]["mvpn-instance-information"][0]["mvpn-instance"][0]["instance-family"][0]["instance-entry"][0]["c-multicast-ipv4"][0]["c-multicast-ipv4-entry"]:
            source2 = entry2["c-multicast-address"][0]["data"].split(":")[0]
            group2 = entry2["c-multicast-address"][0]["data"].split(":")[1]
            tunnelID2 = entry2["provider-tunnel-id"][0]["data"].split(" ")[1]
            mcast[tunnelID2] = {"source": source2, "group":group2}
        for entry in data[device]["mpls-lsp-information"][0]["rsvp-session-data"][0]["rsvp-session"]:
            daddr = entry["mpls-lsp"][0]["destination-address"][0]["data"]
            saddr = entry["mpls-lsp"][0]["source-address"][0]["data"]
            state = entry["mpls-lsp"][0]["lsp-state"][0]["data"]
            lspPackets = entry["mpls-lsp"][0]["lsp-packets"][0]["data"]
            lspBytes = entry["mpls-lsp"][0]["lsp-bytes"][0]["data"]
            name = entry["mpls-lsp"][0]["name"][0]["data"]
            searchName = ":".join([str(item) for item in name.split(":")[1:] ] )
            if ":mvpn" not in searchName:
                source = mcast[searchName]["source"].split("/32")[0]
                group = mcast[searchName]["group"].split("/32")[0]
            else:
                source = "None"
                group = "None"
            send_string="ingress,state=%s,name=%s,saddr=%s,daddr=%s,mcastSource=%s,mcastGroup=%s lspPackets=%s,lspBytes=%s" % (state,name,saddr,daddr,source,group,lspPackets.replace(" ",""),lspBytes.replace(" ",""))
            sock.sendto(bytes(send_string, "utf-8"), ("127.0.0.1", 8089))
            #print(send_string)
    bastionConnect.close()




def main():
    count =  0
    os.system("clear")
    while True:
        if datetime.now().strftime("%M")[-1] == "0" or datetime.now().strftime("%M")[-1] == "5":
            try:
                connections(devices,userName,passWord)
            except Exception as e:
                logging.error(traceback.format_exc())
            count = count + 1
            print(datetime.now().strftime("%d-%m-%Y::%H:%M:%S") + "\tNow at Cycle\t" + str(count))
            time.sleep(61)
        else:
            time.sleep(1)


if __name__ == "__main__":
    main()
