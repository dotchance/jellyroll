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
#getPatternFileData = '{"cmd":"toCtlrGet", "get":[["patternFileData", "Legacy", "Red Yellow Green Blue"]]}'
#setZonePattern  = '{"cmd":"toCtlrSet","runPattern":{"file":"Christmas/Christmas Tree","data":"","id":"","state":1,"zoneName":["Zone", "Zone1"]}}'
#runPattern      = '{"cmd":"toCtlrSet","runPattern":{"file":””,"data":"{\"colors\":[<int>,<int>,<int>],\"spaceBetweenPixels\":<int>,\"effectBetweenPixels\":<effect>,\"type\":<type>,\"skip\":<int>,\"numOfLeds\":<int>,\"runData\":{\"speed\":<int>,\"brightness\":<int>,\"effect\":<effect>,\"effectValue\":<int>,\"rgbAdj\":[<int>,<int>,<int>]},\"direction\":<direction>}","id":"","state":<int>,"zoneName":[<zone>,<zone>]}}'

zoneBrightnessLevel = ''

def wsOpen(controllerURL, headers):
    print('Attempting connection to: %s........' % controllerURL, end = '')  
    #websocket.enableTrace(args.verbose)
        
    try:
        ws = websocket.create_connection(controllerURL, header=headers)
    except Exception as e:
        print('FAILURE: Failed to open connection to controller: %s' % controllerURL)
        print(e)
        sys.exit(1)
    print('connection esablished.')
    
    return ws

def wsClose(ws, controllerURL):
    print('Closing connection to: %s' % controllerURL)
    try:
        ws.close()
    except Exception as e:
        print('Failed to close connection: %s' % (e))
    return

def wsSendCommand(ws, cmd):
    try:
    #    print('Sending command: %s    ....' % cmd, end = '')
        ws.send(cmd)
    #    print('sent')
    except Exception as e:
        print('Failed to send command: %s' % (e))
        return

    try:
    #    print('Listening for response....." , end = '')
        wsResponse = ws.recv()
    #    print("response recieved: %s" % wsResponse)
    except Exception as e:
        print('Failed to receive: %s' % (e))
        return

    return wsResponse

def jsonToListPatternFoldersAndNames(jsonObject):
    dataArray = []
    for value in jsonObject["patternFileList"]:
        dataToStore = value['folders']+'/'+value['name']
        dataArray.append(dataToStore)

    return dataArray

def testfunc(ws, keys):
    
    patternData = json.loads(wsSendCommand(ws, getPatternFileList))

    dataArray = []
    for value in patternData["patternFileList"]:
        string = ''
        for key in keys:
            string += value[key]+'/'
        dataArray.append(string.replace('//','/'))
    return dataArray

def getZoneNames(ws):
    print('Getting zone list from controller..' , end = '')
    zoneData = json.loads(wsSendCommand(ws, getAllZones))

    for zone in zoneData.get('zones').keys():
        print("    {}".format(zone))
    return

def getPatternData(ws):
    print('Getting pattern list from controller.....')

    patternData = json.loads(wsSendCommand(ws, getPatternFileList))

    # patternData is a dict that contains
    #   k: cmd                v: fromCtlr
    #   k: patternFileList    v: [{'folders': 'folderName', 'name': 'patternName', 'readOnly': False}, {'folders': 'folderName', 'name': 'patternName', 'readOnly': True}, ..., ]

    patternFileList = jsonToListPatternFoldersAndNames(patternData)
    patternFileList.sort()

    for pattern in patternFileList:
        print(pattern)

    return patternFileList

def setZoneOnOff(ws, zoneName, zoneOnOff):
    print('Turning zone %s %s' % (zoneName, zoneOnOff))

    zoneOnOffCmd = '{"cmd":"toCtlrSet","runPattern":{"file":"","data":"","id":"","state":%s,"zoneName":["%s"]}}' % (zoneOnOff, zoneName)
    zoneOnOffResult = json.loads(wsSendCommand(ws, zoneOnOffCmd))

    return zoneOnOffResult

def setZonePattern(ws, zoneName, patternName):

    zonePatternCmd = '{"cmd":"toCtlrSet","runPattern":{"file":"%s","data":"","id":"","state":'',"zoneName":["%s"]}}' % (patternName, zoneName)
    zonePatternResult = json.loads(wsSendCommand(ws, zonePatternCmd))

    return zonePatternResult

def setZoneBrightness(ws, zoneName, zoneBrightnessLevel):
    zoneBrightnessCmd = '{"cmd":"toCtlrSet","runPattern":{"file":"%s","data":"","id":"","state":'',"zoneName":["%s"]}}' % (patternName, zoneName)
    zoneBrigthnessResult = json.loads(wsSendCommand(ws, zoneBrightnessCmd))

    return zoneBrightnessResult

def main(args): 
    controllerURL   = 'ws://%s:%s/ws/' % (args.controllerIP, args.controllerPort)
    headers         = {'user-agent': '%s (%s)' % (appName, appVersion)}

    if "getZoneNames" in sys.argv:
        print("Found getZoneNames in arguments - attempting to get list of Zones")
        ws = wsOpen(controllerURL, headers)
        zoneNames = getZoneNames(ws)
        
    elif "getPatterns" in sys.argv:
        print("Found getPatterns in arguments - attempting to get list of Patterns")
        ws = wsOpen(controllerURL, headers)
        patternFileList = getPatternData(ws)
        #keys = ['name', 'readOnly']
        #patternFileList = testfunc(ws, keys)
        print(patternFileList)

    elif "setZone" in sys.argv:
        print("Found setZone in arguments - attempting to control a zone.")
        ws = wsOpen(controllerURL, headers)
        zoneName        = args.zoneName
        patternName     = args.patternName
        zoneOnOff       = args.zoneOnOff
        setZoneOnOff(ws, zoneName, zoneOnOff)
    
    else:
        print("NO COMMANDS FOUND - DOING NOTHING")
    
    wsClose(ws, controllerURL)
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
    
    parser_getZone = subparsers.add_parser('getZoneNames')
    parser_getPatterns = subparsers.add_parser('getPatterns')

    try:
        sys.exit(main(parser.parse_args()))
    except (SystemExit, KeyboardInterrupt): 
        raise 
    except Exception as e: 
        print("Error: " + str(e))
