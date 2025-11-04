"""Serialização binária para Mission Link (UDP)"""

import struct

def serialize_request():
    res='1'.encode('utf8')
    #serializar request
    return

def serialize_ack():
    res='2'.encode('utf8')
    #serializar ack
    return

def serialize_task(tasl_id):
    return

def serialize_mission(mission_id, area, task_id, duration):
    res='3'.encode('utf8')
    
    res+=mission_id.encode('utf8').ljust(5, b'\0')

    res+=struct.pack('>f', area[0]) 
    res+=struct.pack('>f', area[1]) 
    res+=struct.pack('>f', area[2]) 
    res+=struct.pack('>f', area[3]) 

    res+=serialize_task(task_id)

    res+=duration.to_bytes(4, 'big')

    return res

def serializa_report():
    res='4'.encode('utf8')
    #serializar report
    return


def deserialize_request(data):
    return

def deserialize_ack(data):
    return

def deserialize_mission(data):
    return


def deserialize_report(data):
    return


def deserialize_ml(data):
    
    type = data[0:1].decode('utf-8').rstrip('\0')

    if(type=='1'):
        return deserialize_request(data[1:])
    elif(type=='2'):
        return deserialize_ack(data)
    elif(type=='3'):
        return deserialize_mission(data)
    elif(type=='4'):
        return deserialize_report(data)
    
