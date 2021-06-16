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
    return zoneDataDict.get('zones').keys()


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

def setZoneOnOff(ws, zoneName, patternName, zoneOnOff):
    print('Turning zone %s %s' % (zoneName, zoneOnOff))
    cmd = '{"cmd":"toCtlrSet","runPattern":{"file":"%s","data":"","id":"","state":%s,"zoneName":["%s"]}}' % (patternName, zoneOnOff, zoneName)
    print(cmd)
    ws.send(cmd)
    result = ws.recv()
    print(result)
    return result

def setZoneBrightness(ws, zone):
    pass

def setZonePattern(ws, zone, patternName):
    pass


def main(args): 
    controllerURL   = 'ws://%s:%s/ws/' % (args.controllerIP, args.controllerPort)
    headers         = {'user-agent': '%s (%s)' % (appName, appVersion)}
    #websocket.enableTrace(args.verbose)
    ws = openWS(controllerURL, headers)

    if "getZones" in sys.argv:
        print("Found getZones in arguments - attempting to get list of Zones")
        print(getZoneDataAsDict(ws))
        
    elif "getPatterns" in sys.argv:
        print("Found getPatterns in arguments - attempting to get list of Patterns")
        print(getPatternDataAsDict(ws))
    
    elif "setZone" in sys.argv:
        print("Found setZone in arguments - attempting to control a zone.")
        zoneName    = args.zoneName
        patternName = args.patternName
        zoneOnOff   = args.zoneOnOff
        setZoneOnOff(ws, zoneName, patternName, zoneOnOff)
    
    else:
        print("NO COMMANDS FOUND - CLOSING CONNECTION")
    
    closeWS(ws, controllerURL)
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='jellyroll.py: Send commands to JellyFish Lighting controller')
    parser.add_argument('-c', '--controllerIP', type=str, required=True, help='hostname or IP address of JellyFish controller')
    parser.add_argument('-p', '--controllerPort', type=str, required=False, default='9000', help='port number that controller is listening on. Typically 9000')
    parser.add_argument('-v', '--verbose', type=bool, required=False, default=False, help='enable verbose logging')

    subparsers = parser.add_subparsers(title='COMMANDS', description='List of sub commands that can be run - each has thier own required options')
    parser_setZone = subparsers.add_parser('setZone')
    parser_setZone.add_argument('-z', '--zoneName', type=str, required=True, default=argparse.SUPPRESS, help='Name of Zone to control')
    parser_setZone.add_argument('-o', '--zoneOnOff', type=str, required=False, default=argparse.SUPPRESS, help='turn Zone on (1) or off (0)')
    parser_setZone.add_argument('-t', '--patternName', type=str, required=False, default='Warm Cool/White', help='name of the pattern that you want to apply format: Folder/Pattern Name') 
    
    parser_getZone = subparsers.add_parser('getZones')
    parser_getPatterns = subparsers.add_parser('getPatterns')

    try:
        sys.exit(main(parser.parse_args()))
    except (SystemExit, KeyboardInterrupt): 
        raise 
    except Exception as e: 
        print("Error: " + str(e))
