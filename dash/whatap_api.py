"""{"type":"mxql","pcode":2,"params":{"pcode":2,"stime":1675923960000,"etime":1675927560000,"trigger":0,
"mql":"CATEGORY tcpSessionState\nTAGLOAD\nSELECT \'DestinationIP\', \'DestinationPort\',\'Pid\',\n\'Direction\', \n\'Avg Jitter\',\n\'Avg Latency\',\n\'Max Jitter,\n\'Max Latency\',\n\'Min Jitter\',\n\'Min Latency\',\n\'RecvByte\',\n\'RecvCount\',\n\'SendByte\',\n\'SendCount\',\n\'SessionCount\'\nFILTER { key:Direction, value: \\"IN\\" }\nFILTER { key:Pid, exist: true }\n\nCREATE { key:_id_, expr: \\"DestinationIP+\'_\'+Pid\\" }\nGROUP { timeunit: 5s, pk: _id_ }\nUPDATE { key: [\\"Avg Jitter\\",\\"Avg Latency\\",\\"Max Jitter\\",\\"Max Latency\\",\\"Min Jitter\\",\\"Min Latency\\",\\"RecvByte\\",\\"RecvCount\\",\\"SendByte\\",\\"SendCount\\",\\"SessionCount\\"], value: \'avg\' }\n",
"limit":100,"userId":"admin@whatap.io","pageKey":"mxql","param":{"$etime":1675927560000}},
"path":"text","authKey":""}"""

import requests
import logging

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

headers = {'Cookie':'global.skin=wh; lang=ko; JSESSIONID=KQTl4obn8epXQOOloUKGvB3_U1Fim-kXkBMOHoNX; wa="W/Kz829oWnH9XO5deG5iPUZhX2a+ZNj/PECnlMQa9FmUcymuIQ6uwS7L7T9Y5laPYl/BVLWAkMs="'}

import time

def getQuery(pcode, stime, etime, limit=99999, url='http://ec2-54-180-154-217.ap-northeast-2.compute.amazonaws.com:8080/yard/api/flush', headers = headers):
    body = {"type":"mxql","pcode":pcode,"params":{"pcode":pcode,"stime":stime,"etime":etime,"trigger":0,
    "mql":"""CATEGORY tcpSessionState
TAGLOAD
SELECT 'DestinationIP','DestinationPort', 'SourceIP', 'SourcePort','Pid',
'SourceHostTagName','SourceProcessTagName','SourceProcessTypeTagName',
'Direction', 
'Avg Jitter',
'Avg Latency',
'Max Jitter,
'Max Latency',
'Min Jitter',
'Min Latency',
'RecvByte',
'RecvCount',
'SendByte',
'SendCount',
'SessionCount'
FILTER { key:Pid, exist: true }
CREATE { key:_id_, expr: "SourceIP+'_'+Pid" }
GROUP { timeunit: 5s, pk: _id_ }
UPDATE { key: ["Avg Jitter","Avg Latency","Max Jitter","Max Latency","Min Jitter","Min Latency","RecvByte","RecvCount","SendByte","SendCount","SessionCount"], value: 'avg' }
""",
    "limit":limit,"userId":"","pageKey":"mxql","param":{"$etime":etime}},
    "path":"text","authKey":""}

    r = requests.post(url,headers = headers, json=body)
    return r.json()


if __name__ == '__main__':
    pcode = 2
    
    etime = int(time.time()*1000) - 1000*60*60*2 
    stime =etime- 1000*60*60*1 
    stime = 1675923960000
    etime = 1675927560000
    resp = getQuery(pcode, stime, etime)
    from pprint import pprint
    pprint(resp)