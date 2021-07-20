#@sidharth.mohapatra@honeywell.com
#dt:11th July 2021
#API Integrator for Openshift Quota Automation

from typing import Optional
from fastapi import FastAPI,status,Depends, Request , Header
from pydantic import BaseModel
import http.client
import json
import os



#Create Namespace Quota
def createQuota(clusterAPI,nameSpace,cpuLimit,memoryLimit,cpuRequest,memoryRequest,quotaName):
    url = "/api/v1/namespaces/"+nameSpace+"/resourcequotas"
    conn = http.client.HTTPSConnection(clusterAPI, 6443)
    payload = json.dumps({
    "kind": "ResourceQuota",
    "apiVersion": "v1",
    "metadata": {
    "name": quotaName
    },
    "spec": {
    "hard": {
      "limits.cpu": cpuLimit,
      "limits.memory": memoryLimit,
      "requests.cpu": cpuRequest,
      "requests.memory": memoryRequest
    }
    }
    })
 
    headers = {
    'Accept': 'application/json',
    'Connection': 'close',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+os.getenv('token')
    }
    conn.request("POST",url, payload, headers)
    res = conn.getresponse()
    data = res.read()
    response = data.decode("utf-8")
    return response

#Update Namespace Quota with new values
def updateQuota(clusterAPI,nameSpace,cpuLimit,memoryLimit,cpuRequest,memoryRequest,quotaName):
    url = "/api/v1/namespaces/"+nameSpace+"/resourcequotas/"+quotaName
    conn = http.client.HTTPSConnection(clusterAPI, 6443)
    payload = json.dumps({
    "kind": "ResourceQuota",
    "apiVersion": "v1",
    "metadata": {
    "name": quotaName
    },
    "spec": {
    "hard": {
      "limits.cpu": cpuLimit,
      "limits.memory": memoryLimit,
      "requests.cpu": cpuRequest,
      "requests.memory": memoryRequest
    }
    }
    })
 
    headers = {
    'Accept': 'application/json',
    'Connection': 'close',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+os.getenv('token')
    }
    conn.request("PUT",url, payload, headers)
    res = conn.getresponse()
    data = res.read()
    response = data.decode("utf-8")
    return res.status

def deleteQuota(clusterAPI,nameSpace,cpuLimit,memoryLimit,cpuRequest,memoryRequest,quotaName):
    url = "/api/v1/namespaces/"+nameSpace+"/resourcequotas/"+quotaName
    conn = http.client.HTTPSConnection(clusterAPI, 6443)
    payload = ''
    headers = {
    'Accept': 'application/json',
    'Connection': 'close',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer '+os.getenv('token')
    }
    conn.request("DELETE",url, payload, headers)
    res = conn.getresponse()
    data = res.read()
    response = data.decode("utf-8")
    return res.status

#Check existing Quota in the Namespace
def checkQuota(clusterAPI,nameSpace):
    url = "/api/v1/namespaces/"+nameSpace+"/resourcequotas"
    conn = http.client.HTTPSConnection(clusterAPI, 6443)
    payload = ''
    headers = {
  	'Accept': 'application/json',
  	'Connection': 'close',
  	'Content-Type': 'application/json',
  	'Authorization': 'Bearer '+os.getenv('token')
	}
        
    conn.request("GET", url, payload, headers)
    res = conn.getresponse()
    data = res.read()
    data1 = json.loads(data)
    if data1.get('items') == []:
        qname = ''
        lmemory = ''
        lcpu = ''
        return 200,qname,lmemory,lcpu
    else:
        qname = str(data1['items'][0]['metadata']['name'])
        lmemory = str(data1['items'][0]['status']['hard']['limits.memory'])
        lcpu = str(data1['items'][0]['status']['hard']['limits.cpu'])
        return 404,qname,lmemory,lcpu


class Quota(BaseModel):
    cluster: str
    environment: str
    namespace: str
    cpuLimit: float
    memoryLimit: float
    cpuRequest: float
    memoryRequest: float


app = FastAPI()


@app.post("/quota/",status_code=status.HTTP_200_OK)
async def create_quota(quota: Quota,x_token: str = Header(None)):
    if x_token == 'client':
        if quota.environment == 'US-Prod':
            clusterAPI=os.getenv('USProdAPI')
            status,qname,lmemory,lcpu = checkQuota(clusterAPI,quota.namespace)
            if status == 404:
                if float(lmemory) <= quota.memoryLimit and float(lcpu) <= quota.cpuLimit:
                        if quota.cpuLimit > 6 and float(lcpu) <= 6 and quota.cpuLimit < 10:
                            quotaName = 'prod-medium-quota'
                            response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                            response = deleteQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Incremented"
                        elif quota.cpuLimit > 10 and float(lcpu) < 10:
                            quotaName = 'prod-large-quota'
                            response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                            response = deleteQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Incremented"
                        else:
                            response = updateQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Updated"
                else:
                    return 'Invalid Quota Request'
            else:
                if quota.cpuLimit > 4 and quota.cpuLimit < 10:
                    quotaName = 'prod-medium-quota'
                elif quota.cpuLimit > 10:
                    quotaName = 'prod-large-quota'
                else:
                    quotaName = 'prod-small-quota'
                    response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                    return "Quota Created"
        if quota.environment == 'EU-Prod':
            clusterAPI=os.getenv('EUProdAPI')
            status,qname,lmemory,lcpu  = checkQuota(clusterAPI,quota.namespace)
            if status == 404:
                if float(lmemory) <= quota.memoryLimit and float(lcpu) <= quota.cpuLimit:
                        if quota.cpuLimit > 6 and float(lcpu) <= 6 and quota.cpuLimit < 10:
                            quotaName = 'prod-medium-quota'
                            response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                            response = deleteQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Incremented"
                        elif quota.cpuLimit > 10 and float(lcpu) < 10:
                            quotaName = 'prod-large-quota'
                            response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                            response = deleteQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Incremented"
                        else:
                            response = updateQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Updated"
                else:
                    return 'Invalid Quota Request'
            else:
                if quota.cpuLimit >= 6 and quota.cpuLimit < 10:
                    quotaName = 'dev-medium-quota'
                elif quota.cpuLimit >= 10:
                    quotaName = 'dev-large-quota'
                else:
                    quotaName = 'dev-small-quota'
                response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                return "Quota Created"
        if quota.environment == 'US-Dev':
            clusterAPI=os.getenv('USDevAPI')
            status,qname,lmemory,lcpu  = checkQuota(clusterAPI,quota.namespace)
            if status == 404:
                if float(lmemory) <= quota.memoryLimit and float(lcpu) <= quota.cpuLimit:
                        if quota.cpuLimit > 6 and float(lcpu) <= 6 and quota.cpuLimit < 10:
                            quotaName = 'dev-medium-quota'
                            response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                            response = deleteQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Incremented"
                        elif quota.cpuLimit > 10 and float(lcpu) < 10:
                            quotaName = 'dev-large-quota'
                            response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                            response = deleteQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Incremented"
                        else:
                            response = updateQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Updated"
                else:
                    return 'Invalid Quota Request'
            else:
                if quota.cpuLimit >= 6 and quota.cpuLimit < 10:
                    quotaName = 'dev-medium-quota'
                elif quota.cpuLimit >= 10:
                    quotaName = 'dev-large-quota'
                else:
                    quotaName = 'dev-small-quota'
                response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                return "Quota Created"
        if quota.environment == 'EU-Dev':
            clusterAPI=os.getenv('EUDevAPI')
            status,qname,lmemory,lcpu  = checkQuota(clusterAPI,quota.namespace)
            if status == 404:
                if float(lmemory) <= quota.memoryLimit and float(lcpu) <= quota.cpuLimit:
                        if quota.cpuLimit > 6 and float(lcpu) <= 6 and quota.cpuLimit < 10:
                            quotaName = 'dev-medium-quota'
                            response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                            response = deleteQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Incremented"
                        elif quota.cpuLimit > 10 and float(lcpu) < 10:
                            quotaName = 'dev-large-quota'
                            response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                            response = deleteQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Incremented"
                        else:
                            response = updateQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,qname)
                            return "Quota Updated"
                else:
                    return 'Invalid Quota Request'
            else:
                if quota.cpuLimit >= 6 and quota.cpuLimit < 10:
                    quotaName = 'dev-medium-quota'
                elif quota.cpuLimit >= 10:
                    quotaName = 'dev-large-quota'
                else:
                    quotaName = 'dev-small-quota'
                response = createQuota(clusterAPI,quota.namespace,quota.cpuLimit,quota.memoryLimit,quota.cpuRequest,quota.memoryRequest,quotaName)
                return "Quota Created"

        else:
            return "Invalid Environment"
    else:
        return "Unauthorised"
