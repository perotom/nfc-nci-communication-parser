#!/usr/bin/python

from argparse import ArgumentParser

def parse(line):
    bytes = bytearray.fromhex(line)
    mt = (bytes[0] & 0b11100000) >> 5
    if mt == 0:
        file1.write("  MT: Data packet\n")
        parseDataPacket(mt, bytes)
    if mt == 1:
        file1.write("  MT: Control packet - CMD\n")
        parseControlPacket(mt, bytes)
    if mt == 2:
        file1.write("  MT: Control packet - RES\n")
        parseControlPacket(mt, bytes)
    if mt == 3:
        file1.write("  MT: Control packet - NTF\n")
        parseControlPacket(mt, bytes)

def parseDataPacket(mt, bytes):
    connId = (bytes[0] & 0b00001111)
    file1.write("  ConnId: " + str(connId) + "\n")
    file1.write("  Payload length: " + str(bytes[2]) + " bytes\n")

def parseControlPacket(mt, bytes):
    gid = (bytes[0] & 0b00001111)
    oid = (bytes[1] & 0b00111111)

    if gid == 0:
        file1.write("  GID: NCI Core\n")
        if oid == 0:
            file1.write("  OID: CORE_RESET\n")
        if oid == 1:
            file1.write("  OID: CORE_INIT\n")
        if oid == 2:
            file1.write("  OID: CORE_SET_CONFIG\n")
        if oid == 3:
            file1.write("  OID: CORE_GET_CONFIG\n")
        if oid == 4:
            file1.write("  OID: CORE_CONN_CREATE\n")
        if oid == 5:
            file1.write("  OID: CORE_CONN_CLOSE\n")
        if oid == 6:
            file1.write("  OID: CORE_CONN_CREDITS\n")
        if oid == 7:
            file1.write("  OID: CORE_GENERIC_ERROR\n")
        if oid == 8:
            file1.write("  OID: CORE_INTERFACE_ERROR\n")
    if gid == 1:
        file1.write("  GID: RF Management\n")
        if oid == 0:
            file1.write("  OID: RF_DISCOVER_MAP\n")
        if oid == 1:
            file1.write("  OID: RF_SET_LISTEN_MODE_ROUTING\n")
        if oid == 2:
            file1.write("  OID: RF_GET_LISTEN_MODE_ROUTING\n")
        if oid == 3:
            file1.write("  OID: RF_DISCOVER\n")
        if oid == 4:
            file1.write("  OID: RF_DISCOVER_SELECT\n")
        if oid == 5:
            file1.write("  OID: RF_INTF_ACTIVATED\n")
        if oid == 6:
            file1.write("  OID: RF_DEACTIVATE\n")
        if oid == 7:
            file1.write("  OID: RF_FIELD_INFO\n")
        if oid == 8:
            file1.write("  OID: RF_T3T_POLLING\n")
        if oid == 9:
            file1.write("  OID: RF_NFCEE_ACTION\n")
        if oid == 10:
            file1.write("  OID: RF_NFCEE_DISCOVERY_REQ\n")
        if oid == 11:
            file1.write("  OID: RF_PARAMETER_UPDATE\n")
    if gid == 2:
        file1.write("  GID: NFCEE Management\n")
        if oid == 0:
            file1.write("  OID: NFCEE_DISCOVER\n")
        if oid == 1:
            file1.write("  OID: NFCEE_MODE_SET\n")
    if gid == 3:
        file1.write("  GID: Proprietary\n")

    file1.write("  Payload length: " + str(bytes[2]) + " bytes\n")

    # further parsing
    if mt == 1: # commands
        if gid == 0 and oid == 2:
            parseCoreConfig(bytes, 3)
        elif gid == 1 and oid == 0:
            parseRfDiscoverMap(bytes)
        elif gid == 1 and oid == 1:
            parseRfSetListenModeRouting(bytes)
        elif gid == 1 and oid == 3:
            parseRfDiscover(bytes)
    elif mt == 2: # responses
        if gid == 0 and oid == 3:
            parseCoreConfig(bytes, 4)
        else:
            if bytes[3] == 0:
                file1.write("  Status: OK\n")
            elif bytes[3] == 1:
                file1.write("  Status: REJECTED\n")
            else:
                file1.write("  Status: OK\n")

def parseCoreConfig(bytes, startIndex):
    params = bytes[startIndex]
    file1.write("  Params: " + str(params) + "\n")
    if params <= 0:
        return
    i = startIndex + 1
    while i < len(bytes):
        paramId = bytes[i]
        i += 1
        paramLen = bytes[i]
        i += 1
        file1.write("  ParamId:  " + getCoreConfigParamName(paramId) + " (" + '0x{:02x}'.format(paramId) + ") length: " + str(paramLen) + "\n")
        file1.write("  ParamVal: " + " ".join('0x{:02x}'.format(x) for x in bytes[i:i+paramLen]) + "\n")
        i += paramLen

def parseRfDiscoverMap(bytes):
    mappings = bytes[3]
    file1.write("  Mappings: " + str(mappings) + "\n")
    i = 4
    while i < len(bytes):
        file1.write("  RF Protocol:     " + getRfProtocol(bytes[i]) + " (" + '0x{:02x}'.format(bytes[i]) + ")" + "\n")
        if bytes[i + 1] == 1:
            file1.write("  Mode:            Poll\n")
        elif bytes[i + 1] == 2:
            file1.write("  Mode:            Listen\n")
        elif bytes[i + 1] == 3:
            file1.write("  Mode:            Poll + Listen\n")
        else:
            file1.write("  Mode:            Unkown\n")
        file1.write("  RF Interface:    " + getRfInterface(bytes[i + 2]) + " (" + '0x{:02x}'.format(bytes[i + 2]) + ")" + "\n")
        i += 3

def parseRfDiscover(bytes):
    configs = bytes[3]
    file1.write("  Configs: " + str(configs) + "\n")
    i = 4
    while i < len(bytes):
        file1.write("  RF Tech & Mode:     " + getRfTechAndMode(bytes[i]) + " (" + '0x{:02x}'.format(bytes[i]) + ")" + "\n")
        file1.write("  Discover frequency: " + str(bytes[i + 1]) + "\n")
        i += 2

def parseRfSetListenModeRouting(bytes):
    routings = bytes[4]
    file1.write("  Routings: " + str(routings) + "\n")
    i = 5
    while i < len(bytes):
        typ = bytes[i]
        i += 1
        length = bytes[i]
        i += 1
        if typ == 0:
            typeName = "Technology-based"
        elif typ == 1:
            typeName = "Protocol-based"
        elif typ == 2:
            typeName = "AID-based"

        file1.write("  Type:  " + typeName + " (" + '0x{:02x}'.format(typ) + ") length: " + str(length) + "\n")
        file1.write("  Value: " + " ".join('0x{:02x}'.format(x) for x in bytes[i:i+length]) + "\n")

        if typ == 0:
            file1.write("         Technology:  " + getRfTechnology(bytes[i + 2]) + "\n")
        elif typ == 1:
            file1.write("         Protocol:  " + getRfProtocol(bytes[i + 2]) + "\n")
        elif typ == 2:
            file1.write("         AID:  " +bytes[i+2:i+length].decode("utf-8")  + "\n")

        getRfTechnology
        
        i += length

def getRfTechAndMode(tech):
    if tech == 0:
        return "NFC_A_PASSIVE_POLL_MODE"
    if tech == 1:
        return "NFC_B_PASSIVE_POLL_MODE"
    if tech == 2:
        return "NFC_F_PASSIVE_POLL_MODE"
    if tech == 3:
        return "NFC_A_ACTIVE_POLL_MODE"
    if tech == 5:
        return "NFC_F_ACTIVE_POLL_MODE"
    if tech == 6:
        return "NFC_15693_PASSIVE_POLL_MODE"
    if tech == 0x80:
        return "NFC_A_PASSIVE_LISTEN_MODE"
    if tech == 0x81:
        return "NFC_B_PASSIVE_LISTEN_MODE"
    if tech == 0x82:
        return "NFC_F_PASSIVE_LISTEN_MODE"
    if tech == 0x83:
        return "NFC_A_ACTIVE_LISTEN_MODE"
    if tech == 0x85:
        return "NFC_F_ACTIVE_LISTEN_MODE"
    if tech == 0x86:
        return "NFC_15693_PASSIVE_LISTEN_MODE"
    return "RFU"

def getRfTechnology(tech):
    if tech == 0:
        return "NFC_RF_TECHNOLOGY_A"
    if tech == 1:
        return "NFC_RF_TECHNOLOGY_B"
    if tech == 2:
        return "NFC_RF_TECHNOLOGY_F"
    if tech == 3:
        return "NFC_RF_TECHNOLOGY_15693"
    return "RFU"

def getRfProtocol(proto):
    if proto == 0:
        return "PROTOCOL_UNDETERMINED"
    if proto == 1:
        return "PROTOCOL_T1T"
    if proto == 2:
        return "PROTOCOL_T2T"
    if proto == 3:
        return "PROTOCOL_T3T"
    if proto == 4:
        return "PROTOCOL_ISO_DEP"
    if proto == 5:
        return "PROTOCOL_NFC_DEP"
    if proto == 6:
        return "PROTOCOL_15693"
    if proto == 0x80:
        return "PROTOCOL_MIFARE_CLASSIC"
    if proto == 0x8A:
        return "PROTOCOL_KOVIO"
    return "UNKOWN"

def getRfInterface(proto):
    if proto == 0:
        return "NFCEE Direct RF Interface"
    if proto == 1:
        return "Frame RF Interface"
    if proto == 2:
        return "ISO-DEP RF Interface"
    if proto == 3:
        return "NFC-DEP RF Interface"
    return "UNKOWN"

def getCoreConfigParamName(paramId):
    if paramId == 0:
        return "TOTAL_DURATION"
    if paramId == 1:
        return "CON_DEVICES_LIMIT"
    if paramId == 8:
        return "PA_BAIL_OUT"
    if paramId == 0x10:
        return "PB_AFI"
    if paramId == 0x11:
        return "PB_BAIL_OUT"
    if paramId == 0x12:
        return "PB_ATTRIB_PARAM1"
    if paramId == 0x13:
        return "PB_SENSB_REQ_PARAM"
    if paramId == 0x18:
        return "PF_BIT_RATE"
    if paramId == 0x19:
        return "PF_RC_CODE"
    if paramId == 0x20:
        return "PB_H_INFO"
    if paramId == 0x21:
        return "PI_BIT_RATE"
    if paramId == 0x22:
        return "PA_ADV_FEAT"
    if paramId == 0x28:
        return "PN_NFC_DEP_SPEED"
    if paramId == 0x29:
        return "PN_ATR_REQ_GEN_BYTES"
    if paramId == 0x2A:
        return "PN_ATR_REQ_CONFIG"
    if paramId == 0x30:
        return "LA_BIT_FRAME_SDD"
    if paramId == 0x31:
        return "LA_PLATFORM_CONFIG"
    if paramId == 0x32:
        return "LA_SEL_INFO"
    if paramId == 0x33:
        return "LA_NFCID1"
    if paramId == 0x38:
        return "LB_SENSB_INFO"
    if paramId == 0x39:
        return "LB_NFCID0"
    if paramId == 0x3A:
        return "LB_APPLICATION_DATA"
    if paramId == 0x3B:
        return "LB_SFGI"
    if paramId == 0x3C:
        return "LB_ADC_FO"
    if paramId == 0x40 or paramId == 0x41 or paramId == 0x42 or paramId == 0x43 or paramId == 0x44 or paramId == 0x45 or paramId == 0x46 or paramId == 0x47 or paramId == 0x48 or paramId == 0x49 or paramId == 0x4A or paramId == 0x4B or paramId == 0x4C or paramId == 0x4D or paramId == 0x4E or paramId == 0x4F:
        return "LF_T3T_IDENTIFIERS"
    if paramId == 0x50:
        return "LF_PROTOCOL_TYPE"
    if paramId == 0x51:
        return "LF_T3T_PMM"
    if paramId == 0x52:
        return "LF_T3T_MAX"
    if paramId == 0x53:
        return "LF_T3T_FLAGS"
    if paramId == 0x54:
        return "LF_CON_BITR_F"
    if paramId == 0x55:
        return "LF_ADV_FEAT"
    if paramId == 0x58:
        return "LI_FWI"
    if paramId == 0x59:
        return "LA_HIST_BY"
    if paramId == 0x5A:
        return "LB_H_INFO_RESP"
    if paramId == 0x5B:
        return "LI_BIT_RATE"
    if paramId == 0x60:
        return "LN_WT"
    if paramId == 0x61:
        return "LN_ATR_RES_GEN_BYTES"
    if paramId == 0x62:
        return "LN_ATR_RES_CONFIG"
    if paramId == 0x80:
        return "RF_FIELD_INFO"
    if paramId == 0x81:
        return "RF_NFCEE_ACTION"
    if paramId == 0x82:
        return "NFCDEP_OP"
    return "UNKOWN"


parser = ArgumentParser()
parser.add_argument("input", type=str, help="Read binary logs")
parser.add_argument("output", type=str, help="Write converted logs")
args = parser.parse_args()

file1 = open(args.output, 'w')
file2 = open(args.input, 'r') 
for line in file2.readlines() : 
    if "NxpNciX" in line:
        hexStr = line.split(">", 1)[1].strip()
        file1.write("> " + " ".join("0x" + hexStr[i:i+2] for i in range(0, len(hexStr), 2)) + '\n')
        parse(hexStr)
        file1.write("\n")

    if "NxpNciR" in line:
        hexStr = line.split(">", 1)[1].strip()
        file1.write("< " + " ".join("0x" + hexStr[i:i+2] for i in range(0, len(hexStr), 2)) + '\n')
        parse(hexStr)
        file1.write("\n")

    if not line.startswith("2020"):
        file1.write(line.strip() + '\n')    

file2.close() 
file1.close() 