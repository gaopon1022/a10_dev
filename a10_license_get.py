import json
import urllib.request
import time
import base64

def request_http(url, header, body="", method="GET"):
    if method == "POST":
        req = urllib.request.Request(url, json.dumps(body).encode(), headers=header)
    else:
        req = urllib.request.Request(url, headers=header, method=method)
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())

def signin_glm():
    mail="xxxxxxxxxx"
    password="xxxxxxxx"
    post_data={"user":{"email": mail,"password": password}}
    url="https://glm.a10networks.com/users/sign_in.json"
    header= {'Content-Type': 'application/json'}
    resp=request_http(url,header,post_data,"POST")
    auth_token=resp['user_token']
    header={
            'Content-Type': 'application/json',
            'X-User-Email': mail,
            'X-User-Token': auth_token
    }
    return header

def get_token(num):
    header = signin_glm()
    url = 'https://glm.a10networks.com/licenses.json'
    resp = request_http(url, header)
    tokens=[e["token"] for e in resp if e["name"].startswith(license_prefix) and  e["remaining_bandwidth"]>0 for i in range(0,int(e["remaining_bandwidth"]/2))]
    if len(tokens)>=num:
        print("licenses all exsisting. using previous licenses.")
        return tokens[:num]

    org_id=resp[0]["organization_id"]
    post_data={"license":{"license_type": "cfw_cap_sub_trial","organization_id": org_id}}
    num_add_license=int((num-len(tokens)+2)/3)
    for i in range(1,num_add_license+1):
        post_data["license"]["name"]=license_prefix +str(i)
        try:
            resp=request_http(url,header,post_data,"POST")
            tokens+=[resp['token']]* min(3,num-len(tokens))
            time.sleep(2)
        except urllib.error.URLError as e:
            print("assigned "+ str(num-len(tokens)) + " alternative token instead")
            tokens+=[alt_token]*(num-len(tokens))
            break
    print(str(len(tokens))+ ' tokens acquired')
    return tokens[:num]

def revoke_activation(header,licenses):
    url='https://glm.a10networks.com/activations.json'
    resp=request_http(url,header)
    act_entries=[{'id':e["id"],'host_name':e['host_name']} for e in resp if e['license_id'] in [l['id'] for l in licenses] ]
    for entry in act_entries:
        url='https://glm.a10networks.com/activations/%s/revoke_activation.json' % entry['id']
        resp=request_http(url,header,"","POST")
        print(entry['host_name'] + ": " +resp['message'])

def release_license():
    print('releasing trial license...')
    license_prefix="Handson_trial_"
    header = signin_glm()
    url='https://glm.a10networks.com/licenses.json'
    resp=request_http(url,header)
    license_entries=[{'id':e["id"],'name':e['name']} for e in resp if e["name"].startswith(license_prefix)]
    revoke_activation(header,license_entries)
    for entry in license_entries:
        url='https://glm.a10networks.com/licenses/%s.json' % entry['id']
        resp=request_http(url,header,method="DELETE")
        print(entry['name'] +": "+resp["message"])
        time.sleep(2)