import whatap_api
import time

ports = {
    "6600":"PROXY",
    "6761":"EUREKA",
    "8800":"GATEWAY",
    "7700":"YARD",
    "6610":"PROXY",
    "7710":"YARD",
    "6789":"KEEPER",
    "18080":"ACCOUNT",
}
def parsePort(portNum):
    if str(portNum) in ports:
        return "{}:{}".format(ports[portNum], portNum)

    return str(portNum)

def parseNodeLabel(n):
    return "{1}:{0}".format(n['SourceIP'], n['SourceHostTagName'])

def getMatrix():
    elements = []
    pcode = 2

    etime = int(time.time()*1000) 
    stime =etime- 1000*60*60*4
    #stime = 1675923960000
    #etime = 1675927560000
    resp = whatap_api.getQuery(pcode, stime, etime)
    sourceNodes = {}
    destNodes = {}
    inbound = filter(lambda x: x['Direction'] == 'IN', resp)
    outbound = filter(lambda x: x['Direction'] == 'OUT', resp)
    
    allnodes = {}
    clientNodes = {}
    for n in inbound:
        sourcePort = n['SourcePort']
        sourceIP = n['SourceIP']
        if sourceIP not in sourceNodes:
            sourceNodes[sourceIP] = {}
        sourceNodes[sourceIP][sourcePort] = True
        destIP = n['DestinationIP']
        clientNodes[destIP]= True

        allnodes[sourceIP] = n

    for n in outbound:
        destIP = n['DestinationIP']
        destPort = n['DestinationPort']
        if destIP not in destNodes:
            destNodes[destIP] = {}
        destNodes[destIP][destPort] = True

        allnodes[destIP] = n

    xWidth = 1000
    yWidth = 1000
    yOffset = 100
    xOffset = 50
    allNodesCount = len(sourceNodes )+len(destNodes)
    evenXDist = (xWidth - xOffset*2) / allNodesCount
    
    for i, sourceIP in enumerate(sourceNodes.keys()):
        label = "SOURCE: "+parseNodeLabel(allnodes[sourceIP]) + " id:"+sourceIP
        parentNode = { 'group':'nodes', 'data': {'id': sourceIP, 'label': label}}
        elements.append(parentNode)
    for destIP in destNodes.keys():
        if destIP in sourceNodes:
            continue
        label ="DEST: "+ parseNodeLabel(allnodes[destIP]) + " id:"+destIP
        parentNode = { 'group':'nodes','data': {'id': destIP, 'label': label}}
        #elements.append(parentNode)
    
    x = xOffset
    y = yOffset
    targets = {}

    for clientIP in clientNodes.keys():
        parentNode = { 'group':'nodes',
            'data': {'id': clientIP, 'label': "C_{}".format(clientIP)}
            ,'position':dict(x=x, y=y) }
        elements.append(parentNode)
        targets[clientIP]=True
        x += evenXDist

    y += yOffset
    x = xOffset
    for (sourceIP, sourcePorts) in sourceNodes.items():
        #print("nodeCount:", nodesCount, nodeHeight)
        for i, sourcePort in enumerate(sourcePorts):
            nodeid = sourceIP+"_"+sourcePort
            targets[nodeid] = True
            
            childNode = {
                'group':'nodes',
                'data': {'id': nodeid, 
                    'label': parsePort(sourcePort), 
                    'parent': sourceIP}
                , 'position':dict(x=x, y=y)
            }
            
            elements.append(childNode)
            x += evenXDist
    x = xOffset
    y += yOffset
    for (destIP, destPorts) in destNodes.items():
        #print("nodeCount:", nodesCount, nodeHeight)
        for i, destPort in enumerate(destPorts):
            
            nodeid = destIP+"_"+destPort
            targets[nodeid] = True
            childNode = {
                'group':'nodes',
                'data': {'id': nodeid, 
                    'label': parsePort(destPort), 
                    'parent': destIP}
                ,'position':dict(x=x, y=y)
            }
            
            # elements.append(childNode)
            x += evenXDist
    
    inbound = filter(lambda x: x['Direction'] == 'IN', resp)
    edges = {}

    for n in inbound:
        destIP = n['DestinationIP']
        sourceIP = n['SourceIP']
        sourcePort = n['SourcePort']
        destPort = n['DestinationPort']
        
        # nodeid = target
        # parentNode = { 'data': {'id': destIP, 'label': destIP} }
        elements.append(parentNode)

        source = destIP
        target = "{}_{}".format(sourceIP, sourcePort)
        
        edgeKey = "{}_{}".format(source, target)
        #print("{}->{}".format(source, target), (edgeKey not in edges),( target in targets))
        if (edgeKey not in edges) and (target in targets):
            edge = {
                'group':'edges',
                'data': {'source': source, 'target': target}
            }
            #print("edge:", edge)
            elements.append(edge)
            edges[edgeKey] = True



    return elements

if __name__ == '__main__':
    elements = getMatrix()
    from pprint import pprint
    pprint(elements)