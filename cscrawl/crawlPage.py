import json
import time
import requests
import urllib.request
import threadpool
from queue import Queue

taskQueue = Queue()
threadpool_size = 5
timeout = 1
browsermax = 80000
messageurl = 'http://chai.api.3g.cnfol.com/index.php?r=dynam/getdynamonelist&DynamicID=%s&Version=175&VisitType=1'
url = 'http://chai.api.3g.cnfol.com/index.php?r=dynam/getdynamlist'
data = {'PageNum': '1', 'PageSize': '10', 'UserID': '8536812', 'LoginUserID': '946',
        'CheckCode': '8693360', 'Version': '175', 'VisitType': '1'}
header = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
          'Connection': 'Keep-Alive',
          'Host': 'chai.api.3g.cnfol.com'}
print('start')

class IdAndBrowse:
    def __init__(self, id, browsecount):
        self.id = id
        self.browsecount = browsecount
    def getId(self):
        return self.id
    def getBrowseCount(self):
        return self.browsecount

def geturls():
    for pageNum in range(1, 6) :
        data['PageNum'] = str(pageNum)
        response = requests.post(url, data)
        print(data)
        response.encoding = 'utf-8'
        jsonresponse = json.loads(response.text)
        mergelist = jsonresponse['MerList']
        print(mergelist)
        # d = dict(mergelist)
        # print(json.dumps(d))

        # print(mergelist[0])
        dynamic = mergelist[0]
        # print(dict(dynamic)['Dynamic'])
        dynamics = dict(dynamic)['Dynamic']
        # print(len(dynamics))
        for i in range(0, len(dynamics)):
            print(dict(dynamics[i]))
            message = dict(dynamics[i])
            if int(message['BrowseNum']) < browsermax:
                taskQueue.put(IdAndBrowse(str(message['DynamicID']), int(message['BrowseNum'])))


def do_crawl(id, repeatcount):
   roundcount = 0
   errorcount = 0
   sucesscount = 0
   print('.....in crawl id:' + id + ' repeatcount: ' + str(repeatcount))
   while True:
       try:
           if sucesscount > int(repeatcount):
               break
           else:
               roundcount += 1
               urllib.request.urlopen(messageurl % id, timeout=2)
               sucesscount += 1
       except Exception as e:
          print('connect error at round ', roundcount, ' at message: ',  id, e)
          errorcount += 1
          if(errorcount > 80):
              print('!!!! WARNING!!!!  message  ', id, '   maybe something wrong')
              time.sleep(10)
              errorcount = 0
          else:
              time.sleep(3)
          continue
   print('>>>>>>>>>>>message success %s' % id)


pool = threadpool.ThreadPool(5)

while True:
    geturls()
    if not taskQueue.empty():
        paramList = []
        while not taskQueue.empty():
            # reqs = pool.requests
            paramList = []
            task = taskQueue.get()
            id = task.id
            browsecount = task.browsecount
            print("id: " + task.id + "  browse count: " + str(task.browsecount))
            # for i in browsercount:
            # print('start id ' + dynamicid)
            # # if int(browsercount[i]) < browsermax:
            repeatcount = int((browsermax - browsecount) / 80)
            print(requests.get(messageurl % id).text)
            paramList.append(([id, repeatcount], {}))
        crawlThreads = threadpool.makeRequests(do_crawl, paramList)
        [pool.putRequest(th) for th in crawlThreads]
        pool.wait()
        print('>>>>>>>>round finished ')
    time.sleep(1800)


