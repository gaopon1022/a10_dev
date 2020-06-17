import argparse
import datetime
import time
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# ignore the SSL server Certificate error
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Get the new license and apply it to your vthunder')
parser.add_argument('-u', '--glm_username', default='user@example.com', help='the username for login to your GLM account. Default value is: user1@example.com')
parser.add_argument('-p', '--glm_password', default='p@44w0rD', help='the password for login to your GLM account. Default value is: p@44w0rD')
parser.add_argument('-H', '--a10_host', default='172.31.31.31', help='the username for login to your vthunder. Default value is: 172.31.31.31')
parser.add_argument('-U', '--a10_username', default='admin', help='the username for login to your vthunder. Default value is: admin')
parser.add_argument('-P', '--a10_password', default='a10', help='the password for login to your vthunder. Default value is: a10')

try:
    args = parser.parse_args()
    glm_username = args.glm_username
    glm_password = args.glm_password
    a10_host = args.a10_host
    a10_username = args.a10_username
    a10_password = args.a10_password

except Exception as e:
    print('ArgParser Error: ', e)


def glm_login():
    '''
    Description: Method to log into glm.a10networks.com and return the auth token for follow up api calls.
    '''
    json_header = {'Content-Type': 'application/json'}
    values = """
          {
            "user": {
              "email": "%s",
              "password": "%s"
            }
          }
        """ % (glm_username, glm_password)
    try:
        url = 'https://glm.a10networks.com/users/sign_in.json'
        r = requests.post(url, headers=json_header, data=values, verify=False)
        content = r.content
        parsed_json = json.loads(content)
        user_token = parsed_json['user_token']
        glm_req_header = {
            'Content-Type': 'application/json',
            'X-User-Email': glm_username,
            'X-User-Token': user_token
        }
        return glm_req_header

    except Exception as e:
        print('Error in glm_login: ', e)


def get_new_license_token(glm_req_header):
    '''
    Description: create the new trial license and get the value.
    '''
    try:
        date = datetime.date.today()
        url = 'https://glm.a10networks.com/licenses.json'
        r = requests.get(url, headers=glm_req_header)
        content = r.content
        parsed_json = json.loads(content)
        org_id = parsed_json[0]['organization_id']
        values = """
              {
                "license": {
                  "name": "trial-flexpool-%s",
                  "license_type": "cfw_cap_sub_trial",
                  "organization_id": "%s"
                }
              }
            """ % (date, org_id)
        r = requests.post(url, headers=glm_req_header,data=values, verify=False)
        content = r.content
        parsed_json = json.loads(content)
        token = parsed_json['token']
        return token

    except Exception as e:
        print('Error in get_new_license_token: ', e)


# from here: aXAPI function
def a10_login():
    '''
    Description: Login to your vthunder and get the signature ID.
    '''
    try:
        url = 'https://{}/axapi/v3/auth'.format(a10_host)
        payload = {'credentials': {
            'username': a10_username,
            'password': a10_password}
        }
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, headers=headers, json=payload, verify=False)
        r_payload = json.loads(r.text)
        signature = r_payload['authresponse']['signature']
        if r.status_code == 200:
            print('Successfully logged in!')
            return signature

    except Exception as e:
        print('Error in a10_login: ', e)


def a10_logoff(sign):
    '''
    Description: Logoff from your vthunder.
    '''
    try:
        url = 'https://{}/axapi/v3/logoff'.format(a10_host)
        headers = {'Authorization': 'A10 {}'.format(sign)}
        r = requests.post(url, headers=headers, verify=False)
        if r.status_code == 200:
            print('Successfully logged out!')
            return

    except Exception as e:
        print('Error in a10_logoff: ', e)


def a10_write_memory(sign):
    '''
    Description: write memory.
    '''
    try:
        url = 'https://{}/axapi/v3/write/memory'.format(a10_host)
        headers = {'Authorization': 'A10 {}'.format(sign),
                   'Content-Type': 'application/json'}
        r = requests.post(url, headers=headers, verify=False)
        if r.status_code == 200:
            print('Successfully saved!')
            return

    except Exception as e:
        print('Error in a10_write_memory: ', e)


# clideploy: run some CLI commands and then export as a file
def a10_clideploy(sign, glm_token):
    '''
    Description: re-set the glm-commands and send the new license request.
    '''
    try:
        url = 'https://{}/axapi/v3/clideploy'.format(a10_host)
        headers = {'Authorization': 'A10 {}'.format(sign),
                   'Content-Type': 'application/json'}
        payload1 = {'commandList':
                        ['glm enable-requests', 'glm allocate-bandwidth 2',
                            'glm token {}'.format(glm_token)]}
        requests.post(url, headers=headers, json=payload1, verify=False)
        print('thunder configuration...')
        time.sleep(1)
        payload2 = {'commandList':
                        ['glm send license-request']}
        requests.post(url, headers=headers, json=payload2, verify=False)
        time.sleep(2)
        print('sending license-request...')
        payload3 = {'commandList':
                        ['show license-info']}
        r = requests.post(url, headers=headers, json=payload3, verify=False)
        print('output license-info...')
        if r.status_code == 200:
            with open('show.txt', 'w') as f:
                f.write(r.text)
                print('Successfully done!')

    except Exception as e:
        print('Error in a10_clideploy: ', e)


if __name__ == '__main__':
    glm_req_header = glm_login()
    glm_token = get_new_license_token(glm_req_header)
    print('glm token is: {}'.format(glm_token))
    sign = a10_login()
    a10_clideploy(sign, glm_token)
    a10_write_memory(sign)
    a10_logoff(sign)