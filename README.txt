>python a10_license_get.py -h
usage: a10_license_get.py [-h] [-u GLM_USERNAME] [-p GLM_PASSWORD] [-H A10_HOST] [-U A10_USERNAME] [-P A10_PASSWORD]
 
Get the new license and apply it to your vthunder
 
optional arguments:
  -h, --help            show this help message and exit
  -u GLM_USERNAME, --glm_username GLM_USERNAME
                        the username for login to your GLM account. Default value is: user1@example.com
  -p GLM_PASSWORD, --glm_password GLM_PASSWORD
                        the password for login to your GLM account. Default value is: p@44w0rD
  -H A10_HOST, --a10_host A10_HOST
                        the username for login to your vthunder. Default value is: 172.31.31.31
  -U A10_USERNAME, --a10_username A10_USERNAME
                        the username for login to your vthunder. Default value is: admin
  -P A10_PASSWORD, --a10_password A10_PASSWORD
                        the password for login to your vthunder. Default value is: a10

>python a10_license_get.py -u XXXXXXXX -p XXXXXXXX -H 10.0.0.1 -U XXXXXXXX -P XXXXXXXX
check whether to exist the remaining expired licenses...
...licenses that should be revoked doesn't exist
glm token:A10625cb9c8d will be attached...
Successfully logged in!
thunder configuration...
sending license-request...
output license-info...
Successfully done!
Successfully saved!
Successfully logged out!
 
>python a10_license_get.py -u XXXXXXXX -p XXXXXXXX -H 10.0.0.2 -U XXXXXXXX -P XXXXXXXX
check whether to exist the remaining expired licenses...
...licenses that should be revoked doesn't exist
glm token:A10625cb9c8d will be attached...
Successfully logged in!
thunder configuration...
sending license-request...
output license-info...
Successfully done!
Successfully saved!
Successfully logged out!