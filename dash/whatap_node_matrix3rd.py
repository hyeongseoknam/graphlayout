import whatap_api
import time, math

ports = {
    "3306":"MySQL",
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
centerx = width /2
centery = height /2
r=500
maxnodes = 200
inc = math.pi *2 /float(maxnodes)

for i in range(maxnodes):
    x = r * math.cos(i*inc) + centerx
    y = r * math.sin(i*inc) + centery
    centerpoints.append((x, y))    
# print(centerpoints)
pidx=-1
def getCenterPoint(nodeid):
    global pidx, centerpoints
    pidx +=1
    # print('getCenterPoints: ', centerpoints[pidx])
    return centerpoints[pidx%maxnodes]
    
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

    class SimpleChildNode(object):
        def __init__(self, parent, port, tag):
            self.__parent =parent
            self.__port = port
            self.__tag = tag
            
        
        def getNodeId(self):
            nodeid = '{}_{}'.format(self.__parent.getNodeId(), self.__port)

            return nodeid

        def getPort(self):
            return self.__port

        def getLabel(self):
            if self.__tag:
                return "{}:{}".format(self.__tag, self.__port)
            
            return parsePort(self.__port)

    class SimpleNode(object):
        def __init__(self, ip = None, host=None ):
            if not ip:
                raise Exception('SimpleNode Error')
            self.__ip = ip
            self.__host = host
            self.__childs = {}

        def addPort(self, port, tag=None):
            if port in self.__childs:
                cNode = self.__childs[port]
            else:
                cNode = SimpleChildNode(self, port, tag)
                self.__childs[port] =cNode
            return cNode
        
        def getNodeId(self):
            nodeid = '{}'.format(self.__ip)

            return nodeid

        def getLabel(self):

            if self.__host:
                return self.__host
            return self.__ip

        def getChildNodes(self, onNodeId):
            if not self.__childs:
                return 
            # print('getChildNodes:', self.__childs)
            for i, cNodeKey in enumerate(self.__childs):
                cNode = self.__childs[cNodeKey]
                cNodeId = cNode.getNodeId()
                try:
                    onNodeId(cNode.getNodeId())
                except Exception as e:
                    print(e)
                x, y = getCenterPoint(cNodeId)
            
                yield cNodeId, cNode.getLabel(), self.getNodeId(), (x,y)
                
        def setHost(self, host):
            self.__host = host

    for n in inbound:
        sourcePort = n['SourcePort']
        sourceIP = n['SourceIP']
        sourceHostTag = n['SourceHostTagName']
        sourceProcessTag = n['SourceProcessTagName']
        destIP = n['DestinationIP']
        if not destIP or not sourcePort or not sourceIP or not sourceHostTag or not sourceProcessTag:
            continue
        
        
        if sourceIP not in pNodes:
            pNodes[sourceIP] = SimpleNode(ip = sourceIP, host = sourceHostTag)
            # print("parent node: ", sourceIP, sourceHostTag)
        else:
            pNodes[sourceIP].setHost(sourceHostTag)
        
        cNode = pNodes[sourceIP].addPort(sourcePort, tag= sourceProcessTag)
        
        if destIP not in pNodes:
            pNodes[destIP] = SimpleNode(ip  = destIP)

        edge = {
            'group':'edges',
            'data': {'source': pNodes[destIP].getNodeId(), 'target': cNode.getNodeId()},
            'classes': 'edges'
        }
        k = getEdgeKey(pNodes[destIP].getNodeId(), cNode.getNodeId())
        edges[k] = edge

    for n in outbound:
        sourceIP = n['SourceIP']
        sourceHostTag = n['SourceHostTagName']
        sourceProcessTag = n['SourceProcessTagName']

        destIP = n['DestinationIP']
        destPort = n['DestinationPort']
        if destPort == '38844':
            from pprint import pprint
            pprint(n)
        
        if not destIP or not destPort or not sourceIP or not sourceHostTag or not sourceProcessTag:
            continue
        
        if sourceIP not in pNodes:
            pNodes[sourceIP] = SimpleNode(ip = sourceIP, host = sourceHostTag)
            # print("parent node: ", sourceIP, sourceHostTag)
        else:
            pNodes[sourceIP].setHost(sourceHostTag)
        
        
        if destIP not in pNodes:
            pNodes[destIP] = SimpleNode(ip  = destIP)
        cNode = pNodes[destIP].addPort(destPort)
        edge = {
            'group':'edges',
            'data': {'source': pNodes[sourceIP].getNodeId(), 'target': cNode.getNodeId()},
            'classes': 'edges'
        }
        k = getEdgeKey(pNodes[sourceIP].getNodeId(), cNode.getNodeId())
        edges[k] = edge


    # for n in outbound:
    #     destIP = n['DestinationIP']
    #     destPort = n['DestinationPort']
    #     if destIP not in pNodes:
    #         pNodes[destIP] = SimpleNode(ip = destIP)
    #     cNode = pNodes[destIP].addPort(destPort)
    #     sourceIP = n['SourceIP']
    #     if sourceIP not in pNodes:
    #         pNodes[sourceIP] = SimpleNode(ip = sourceIP)

    #     edge = {
    #         'group':'edges',
    #         'data': {'source': pNodes[sourceIP].getNodeId(), 'target': cNode.getNodeId()}
    #     }
    #     k = getEdgeKey(pNodes[sourceIP].getNodeId(), cNode.getNodeId())
    #     edges[k] = edge

    def onNodeId(nodeid):
        nodeids[nodeid] = True

    for i, nodeIP in enumerate(pNodes.keys()):
        pnode = pNodes[nodeIP]
        nodeid = pnode.getNodeId()
        onNodeId(nodeid)
        label = pnode.getLabel()
        parentNode = { 'group':'nodes', 
            'data': {'id': nodeid, 'label': label}}
        elements.append(parentNode)

        for cnodeid, cnodelabel, pNodeId, (x, y) in pnode.getChildNodes(onNodeId):
            childNode = {
                'group':'nodes',
                'data': {'id': cnodeid, 
                    'label': cnodelabel, 
                    'parent': pNodeId}
                ,'position':dict(x=x, y=y)
            }
            elements.append(childNode)

    elements += edges.values()

    return elements

if __name__ == '__main__':
    elements = getMatrix()
    from pprint import pprint
    pprint(elements)