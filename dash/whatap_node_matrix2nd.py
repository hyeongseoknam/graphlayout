import whatap_api
import time, math

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
        return "{}".format(ports[portNum], portNum)

    return str(portNum)

def parseNodeLabel(n):
    return "{1}:{0}".format(n['SourceIP'], n['SourceHostTagName'])

def getNodeId(ip = None, port= None):
    nodeid = '{}'.format(ip)
    if port:
        nodeid = '{}_{}'.format(nodeid, port)

    return nodeid

width = 1000
height=1000
centerpoints = []    
x = 100
y = 100
offsetx = 100
offsety = 100
for i in range(100):
    centerpoints.append((x, y))    
    if x + offsetx > width:
        x = offsetx
        y += offsety
    else:
        x += offsetx

pidx=-1
def getCenterPoint(nodeid):
    global pidx, centerpoints
    pidx +=1
    print('getCenterPoints: ', centerpoints[pidx])
    return centerpoints[pidx]

def getPortNodes(parentnodeid, nodeip, ports, onNodeId):
    elements = []
    if not ports:
        return elements
    (centerX,centerY) = getCenterPoint(parentnodeid)
    r = 50
    inc = math.pi *2 /len(ports)
    
    for i, p in enumerate(ports):
        portnodeid = getNodeId(ip = nodeip, port=p)
        try:
            onNodeId(portnodeid)
        except Exception as e:
            print(e)
        x = r * math.sin(i*inc) + centerX
        y = r * math.cos(i*inc) + centerY
        childNode = {
            'group':'nodes',
            'data': {'id': portnodeid, 
                'label': parsePort(p), 
                'parent': parentnodeid}
            ,'position':dict(x=x, y=y)
        }
        elements.append(childNode)
    
    return elements
    
def getMatrix():
    elements = []
    pcode = 2

    etime = int(time.time()*1000) 
    stime =etime- 1000*60*60*1
    #stime = 1675923960000
    #etime = 1675927560000
    resp = whatap_api.getQuery(pcode, stime, etime)
    pNodes = {}
    inbound = filter(lambda x: x['Direction'] == 'IN', resp)
    outbound = filter(lambda x: x['Direction'] == 'OUT', resp)
    
    nodeids = {}

    def getEdgeKey(source, target):
        return "{}->{}".format(source, target)
    edges = {}
    for n in inbound:
        sourcePort = n['SourcePort']
        sourceIP = n['SourceIP']
        if sourceIP not in pNodes:
            pNodes[sourceIP] = {}
        pNodes[sourceIP][sourcePort] = True
        destIP = n['DestinationIP']
        if destIP not in pNodes:
            pNodes[destIP] = {}

        source = getNodeId(ip = destIP)
        target = getNodeId(ip = sourceIP, port = sourcePort)

        edge = {
            'group':'edges',
            'data': {'source': source, 'target': target, 'length': 200}
        }
        k = getEdgeKey(source, target)
        edges[k] = edge

    for n in outbound:
        destIP = n['DestinationIP']
        destPort = n['DestinationPort']
        if destIP not in pNodes:
            pNodes[destIP] = {}
        pNodes[destIP][destPort] = True
        sourceIP = n['SourceIP']
        if sourceIP not in pNodes:
            pNodes[sourceIP] = {}

        source = getNodeId(ip = sourceIP)
        target = getNodeId(ip = destIP, port = destPort)

        edge = {
            'group':'edges',
            'data': {'source': source, 'target': target}
        }
        k = getEdgeKey(source, target)
        edges[k] = edge

    def onNodeId(nodeid):
        nodeids[nodeid] = True

    for i, nodeIP in enumerate(pNodes.keys()):
        nodeid = getNodeId(ip=nodeIP)
        onNodeId(nodeid)
        label = "SOURCE: id:"+nodeid
        parentNode = { 'group':'nodes', 
            'data': {'id': nodeid, 'label': label}}
        elements.append(parentNode)
        ports = pNodes[nodeIP]
        elements += getPortNodes(nodeid, nodeIP, ports, onNodeId)
    elements += edges.values()

    return elements

if __name__ == '__main__':
    elements = getMatrix()
    from pprint import pprint
    pprint(elements)