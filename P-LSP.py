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
lspIndex = {}
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

bastionServer = 'h-network.net' #Your Jump host
userName = "HBLiB"
passWord = getpass.getpass()


devices = ["P01","P02"]

def command(commandC,targetC):
    rawString = ""
    stdin, stdout, stderr = targetC.exec_command(commandC)
    for line in stdout.read().split(b'\n'):
        rawString = rawString + line.decode() + "\n"
    jsonC = json.loads(rawString)
    return jsonC

def connections(devices,UserN,pasS):
    passWord = pasS
    bastionConnect=paramiko.SSHClient()
    bastionConnect.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    bastionConnect.connect(bastionServer, username=UserN, password=passWord, port=22)
    srcIP = (bastionServer, 22)
    for device in devices:
        #print("Running on \t"+device )
        target=paramiko.SSHClient()
        destIP = (device, 22)
        bastionTransport = bastionConnect.get_transport()
        bastionChannel = bastionTransport.open_channel("direct-tcpip", destIP, srcIP)
        target.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target.connect(destIP, username=UserN, password=passWord, sock=bastionChannel)
        data[device] = command("show mpls lsp transit statistics | display json",target)
        lspIndex[device] = command("show mpls lsp transit | display json",target)
        target.close()
        for entry in data[device]["mpls-lsp-information"][0]["rsvp-session-data"][0]["rsvp-session"]:
            daddr = entry["destination-address"][0]["data"]
            saddr = entry["source-address"][0]["data"]
            state = entry["lsp-state"][0]["data"]
            lspPktbytes = entry["lsp-pktbytes"][0]["data"]
            lspPackets = entry["lsp-packets"][0]["data"]
            lspBytes = entry["lsp-bytes"][0]["data"]
            name = entry["name"][0]["data"]
            for entryX in lspIndex[device]["mpls-lsp-information"][0]["rsvp-session-data"][0]["rsvp-session"]:
                if entryX["name"][0]["data"] == entry["name"][0]["data"]:
                    labelIn = entryX["label-in"][0]["data"]
                    labelOut = entryX["label-out"][0]["data"]
            send_string="transit,state=%s,name=%s,saddr=%s,daddr=%s,labelIn=%s,labelOut=%s lspPackets=%s,lspBytes=%s" % (state,name,saddr,daddr,labelIn,labelOut,int(lspPackets),int(lspBytes))
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
            print("ran and waiting for next Cycle")
            time.sleep(61)
        else:
            print("not the time\t" + datetime.now().strftime("%M")[-1])
            time.sleep(1)

if __name__ == "__main__":
    main()
