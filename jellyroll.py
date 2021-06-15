#!/usr/bin/env python3

# Copyright 2021 Chance Whaley
# Author: first . last @ gmail
# GitHub: @dotchance


import websocket, json, argparse
import sys
#import os, time, logging

# CONSTANTS 
#
appName         = 'jellyroll'
appVersion      = 20210614.01

# EXAMPLES FROM API DOCS
getAllZones        = '{"cmd": "toCtlrGet", "get": [["zones"]]}'
getPatternFileList = '{"cmd": "toCtlrGet", "get": [["patternFileList"]]}'
getPatternFileData = '{"cmd":"toCtlrGet", "get":[["patternFileData", "Legacy", "Red Yellow Green Blue"]]}'

setZonePattern  = '{"cmd":"toCtlrSet","runPattern":{"file":"Christmas/Christmas Tree","data":"","id":"","state":1,"zoneName":["Zone", "Zone1"]}}'
runPattern      = '{"cmd":"toCtlrSet","runPattern":{"file":””,"data":"{\"colors\":[<int>,<int>,<int>],\"spaceBetweenPixels\":<int>,\"effectBetweenPixels\":<effect>,\"type\":<type>,\"skip\":<int>,\"numOfLeds\":<int>,\"runData\":{\"speed\":<int>,\"brightness\":<int>,\"effect\":<effect>,\"effectValue\":<int>,\"rgbAdj\":[<int>,<int>,<int>]},\"direction\":<direction>}","id":"","state":<int>,"zoneName":[<zone>,<zone>]}}'


def openWS(controllerURL, headers):
    print('Attempting connection to: %s' % controllerURL)  
    try:
        ws = websocket.create_connection(controllerURL, header=headers)
    except Exception as e:
        print('FAILURE: Failed to open connection to controller: %s' % controllerURL)
        print(e)
        sys.exit(1)
    print('connection esablished.')
    return ws

def closeWS(ws, controllerURL):
    print('Closing connection to: %s' % controllerURL)
    ws.close()

def getZoneDataAsDict(ws):
    print('Getting zone list from controller..')
    ws.send(getAllZones)
    try:
        zoneDataDict = json.loads(ws.recv())
    except Exception as e:
        print('Failed to receive: %s' % (e))
        return
 
    print('Zone list recieved.')
    return zoneDataDict

def getPatternDataAsDict(ws):
    print('Getting pattern list from controller..')
    ws.send(getPatternFileList)
    try:
        patternDataDict = json.loads(ws.recv())
    except Exception as e:
        print('Failed to receive: %s' % (e))
        return
 
    print('Pattern list recieved.')
    return patternDataDict

def setZoneOnOff(ws, zone, patternName, command):
    pass

def setZoneBrightness(ws, zone):
    pass

def setZonePattern(ws, zone, patternName):
    pass


def main(args): 
    controllerURL   = 'ws://%s:%s/ws/' % (args.controllerIP, args.controllerPort)
    headers         = {'user-agent': '%s (%s)' % (appName, appVersion)}
    websocket.enableTrace(args.verbose)

    ws = openWS(controllerURL, headers)
    zoneDataDict = getZoneDataAsDict(ws)
    patternDataDict = getPatternDataAsDict(ws)
    closeWS(ws, controllerURL)
    sys.exit(0)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='jellyroll.py: Send commands to JellyFish Lighting controller')
    parser.add_argument('-c', '--controllerIP', type=str, required=True, help='hostname or IP address of JellyFish controller')
    parser.add_argument('-p', '--controllerPort', type=str, required=False, default='9000', help='port number that controller is listening on. Typically 9000')
    parser.add_argument('-z', '--zoneName', type=str, required=False, help='Name of Zone to control')
    parser.add_argument('-o', '--zoneOnOff', type=bool, required=False, help='turn Zone on or off - BOOLEAN')
    parser.add_argument('-v', '--verbose', type=bool, required=False, default=False, help='enable verbose logging')

    try:
        sys.exit(main(parser.parse_args()))
    except (SystemExit, KeyboardInterrupt): 
        raise 
    except Exception as e: 
        print("Error: " + str(e))
