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
centerx = width /5
centery = height /3
r=50
margin=200
maxnodes = 15
inc = math.pi *2 /float(maxnodes)
for k in range(3):
    for j in range(10):
        
        centerpointsthistime = []
        for i in range(maxnodes):
            x = r * math.cos(i*inc) + centerx
            y = r * math.sin(i*inc) + centery
            centerpointsthistime.append((x, y))    
        centerx += r*2+margin
        centerpoints.append(centerpointsthistime)
    centery += r*2
    centerx = width /2            
# 마지막 노드
centery = height / 2
centerx = 2000 
centerpointsthistime = []
for i in range(300):
    x = 400 * math.cos(i*inc) + centerx
    y = 400 * math.sin(i*inc) + centery
    centerpointsthistime.append((x, y))    
centerpoints.append(centerpointsthistime)

pidx=-1
centerpointslen= len(centerpoints)
centerpointdict = {}
nodeiddict = {}
def getCenterPoint(nodeid, isMultiPoint=False):
    global pidx, centerpoints,centerpointslen
    if isMultiPoint:
        if nodeid not in centerpointdict:
            centerpointdict[nodeid] = -1
            nodeiddict[nodeid] = len(nodeiddict)
        centerpointdict[nodeid] += 1
        print(nodeiddict[nodeid], centerpointdict[nodeid])
        return centerpoints[nodeiddict[nodeid] % len(centerpoints)][centerpointdict[nodeid]%maxnodes]
    else:
        if 'last' not in centerpointdict:
            centerpointdict['last'] = -1
        centerpointdict['last'] += 1
        return centerpoints[centerpointslen-1][centerpointdict['last']%len(centerpoints[centerpointslen-1])]
    pidx +=1
    # print('getCenterPoints: ', centerpoints[pidx])
    return centerpoints[pidx%centerpointslen]

maxnodes_ex = 100
r_ex=500
centerpoints_ex = []
inc = math.pi *2 /float(maxnodes_ex)
for i in range(int(maxnodes_ex/4), maxnodes_ex):
    x = r_ex * math.cos(i*inc) + centerx
    y = r_ex * math.sin(i*inc) + centery
    centerpoints_ex.append((x, y))    
# print(centerpoints)
pidx_ex=-1

def getCenterPointEx(nodeid):
    global pidx_ex, centerpoints_ex
    pidx_ex +=1
    # print('getCenterPoints: ', centerpoints[pidx])
    return centerpoints_ex[pidx_ex%maxnodes_ex]

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
        def __init__(self, parent, pid, tag, port):
            self.__parent =parent
            self.__pid = pid
            self.__tag = tag
            self.__port = port
        
        def getNodeId(self):
            nodeid = '{}_{}'.format(self.__parent.getNodeId(), self.__pid)

            return nodeid

        def getLabel(self):
            if self.__tag:
                return "{}".format(self.__tag, self.getNodeId())
            #print('getLabel ', self)
            return parsePort(self.__port)

        def getPort(self):
            return self.__port

        def getPid(self):
            return self.__pid

        def __str__(self):
            return "{} {} {} {}".format(self.__parent.getNodeId(),
            self.__pid,
            self.__tag,
            self.__port)

    class SimpleNode(object):
        def __init__(self, ip = None, host=None ):
            if not ip:
                raise Exception('SimpleNode Error')
            self.__ip = ip
            self.__host = host
            self.__childs = {}

        def findChildByPort(self, port):
            for cnode in self.__childs.values():
                if cnode.getPort() == port:
                    return cnode

            return None
        
        def findChildByPid(self, pid):
            for cnode in self.__childs.values():
                print('findChildByPid ',self.__ip, cnode.getPid(), pid, cnode.getPid() == pid)
                if cnode.getPid() == pid:
                    return cnode

            return None

        def addProcess(self, port, pid = None, tag=None):
            if not pid :
                cNode = self.findChildByPort(port)
                if not cNode:
                    cNode = SimpleChildNode(self, pid, tag, port)
                    self.__childs[port] =cNode
            elif pid in self.__childs:
                cNode = self.__childs[pid]
            else:
                cNode = SimpleChildNode(self, pid, tag, port)
                self.__childs[pid] =cNode
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
            isMultiChild= len(self.__childs) > 1
            # print('getChildNodes:', self.__childs)
            for i, cNodeKey in enumerate(self.__childs):
                cNode = self.__childs[cNodeKey]
                cNodeId = cNode.getNodeId()
                try:
                    onNodeId(cNode.getNodeId())
                except Exception as e:
                    print(e)
                x, y = getCenterPoint(self.getNodeId(), isMultiChild)
            
                yield cNodeId, cNode.getLabel(), self.getNodeId(), (x,y)
                
        def setHost(self, host):
            self.__host = host
        
        def onPosition(self, setPosition):
            if not self.__childs and not self.__host:
                x, y = getCenterPointEx(self.getNodeId())
                setPosition(x,y)

    for n in inbound:
        sourcePort = n['SourcePort']
        sourceIP = n['SourceIP']
        sourceHostTag = n['SourceHostTagName']
        sourceProcessTag = n['SourceProcessTagName']
        destIP = n['DestinationIP']
        pid = n['Pid']
        if not pid or not destIP or not sourcePort or not sourceIP or not sourceHostTag or not sourceProcessTag:
            continue
        
        if sourceIP not in pNodes:
            pNodes[sourceIP] = SimpleNode(ip = sourceIP, host = sourceHostTag)
            # print("parent node: ", sourceIP, sourceHostTag)
        else:
            pNodes[sourceIP].setHost(sourceHostTag)
        
        cNode = pNodes[sourceIP].addProcess(sourcePort, pid = pid, tag= sourceProcessTag)
        
        if destIP not in pNodes:
            pNodes[destIP] = SimpleNode(ip  = destIP)

        if destIP != sourceIP:
            edge = {
                'group':'edges',
                'data': {'source': pNodes[destIP].getNodeId(), 'target': cNode.getNodeId()},
                'classes': 'edges'
            }
            k = getEdgeKey(pNodes[destIP].getNodeId(), cNode.getNodeId())
            edges[k] = edge

    for n in outbound:
        sourcePort = n['SourcePort']
        sourceIP = n['SourceIP']
        sourceHostTag = n['SourceHostTagName']
        sourceProcessTag = n['SourceProcessTagName']
        pid = n['Pid']
        destIP = n['DestinationIP']
        destPort = n['DestinationPort']
        
        if not pid or not destIP or not destPort or not sourceIP or not sourceHostTag or not sourceProcessTag:
            continue
        
        if sourceIP not in pNodes:
            pNodes[sourceIP] = SimpleNode(ip = sourceIP, host = sourceHostTag)
            # print("parent node: ", sourceIP, sourceHostTag)
        else:
            pNodes[sourceIP].setHost(sourceHostTag)
        sNode = pNodes[sourceIP].addProcess(sourcePort, pid=pid, tag=sourceProcessTag)    
        
        if destIP not in pNodes:
            pNodes[destIP] = SimpleNode(ip  = destIP)
        tNode = pNodes[destIP].addProcess(destPort)
        if not tNode:
            print('tNode not found for port:', destPort)
            continue
        edge = {
            'group':'edges',
            'data': {'source': sNode.getNodeId(), 'target': tNode.getNodeId()},
            'classes': 'edges'
        }
        k = getEdgeKey(sNode.getNodeId(), tNode.getNodeId())
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
        def setPosition(x,y):
            parentNode['position'] = dict(x = x, y= y)
        pnode.onPosition(setPosition)
        elements.append(parentNode)

        for cnodeid, cnodelabel, pNodeId, (x, y) in pnode.getChildNodes(onNodeId):
            childNode = {
                'group':'nodes',
                'data': {'id': cnodeid, 
                    'label': cnodelabel, 
                    'parent': pNodeId}
            }
            if 'position' not  in parentNode:
                childNode['position'] = dict(x=x, y=y)
            elements.append(childNode)

    elements += edges.values()

    return elements

if __name__ == '__main__':
    elements = getMatrix()
    from pprint import pprint
    pprint(elements)