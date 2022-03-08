#!/usr/bin/env python

import os
import sys
import json
import boto3
import webbrowser
import urllib.request

from urllib.parse import urlencode

AWS_SIGNIN_URL = "https://signin.aws.amazon.com/federation"
AWS_CONSOLE_URL = "https://console.aws.amazon.com/console/home"

def assume_role(key, secret):
    os.environ["AWS_ACCESS_KEY_ID"] = key
    os.environ["AWS_SECRET_ACCESS_KEY"] = secret
    os.environ["AWS_SESSION_TOKEN"] = ''
    sts_client = boto3.client('sts', region_name="eu-west-1", endpoint_url="https://sts.eu-west-1.amazonaws.com")
    account_id = sts_client.get_caller_identity().get('Account')
    assumed_role_object = sts_client.assume_role(
        RoleArn=f"arn:aws:iam::{account_id}:role/workshop-setup/workshop-role",
        RoleSessionName="AssumedWorkshopSession",
        DurationSeconds=21600,
    )
    return assumed_role_object

def get_url(token, destination=AWS_CONSOLE_URL):
    url_params = {
        "Action": "getSigninToken",
        "Session": json.dumps(
            {
                "sessionId": token['Credentials']['AccessKeyId'],
                "sessionKey": token['Credentials']['SecretAccessKey'],
                "sessionToken": token['Credentials']['SessionToken']
            }
        )
    }
    result = urllib.request.urlopen(AWS_SIGNIN_URL + "?" + urlencode(url_params))
    signin_token = json.loads(result.read())['SigninToken']

    url_params = {
        "Action": "login",
        "Destination": destination,
        "SigninToken": signin_token
    }
    return AWS_SIGNIN_URL + "?" + urlencode(url_params)

def print_env_variable(token):
    print(f"export AWS_ACCESS_KEY_ID={token['Credentials']['AccessKeyId']}")
    print(f"export AWS_SECRET_ACCESS_KEY={token['Credentials']['SecretAccessKey']}")
    print(f"export AWS_SESSION_TOKEN={token['Credentials']['SessionToken']}")
    print(f"export AWS_DEFAULT_REGION=eu-west-1")
    print(f"export AWS_REGION=eu-west-1")

def get_keys():
    key = os.environ.get('DNS_AWS_ACCESS_KEY')
    secret = os.environ.get('DNS_AWS_SECRET_KEY')
    if key is None or secret is None:
        print("DNS_AWS_ACCESS_KEY and DNS_AWS_SECRET_KEY should be set")
        return
    return (key, secret)

def main():
    key, secret = get_keys()
    token = assume_role(key, secret)
    if len(sys.argv) > 1 and sys.argv[1] == "console":
        url = get_url(token)
        print(url)
        webbrowser.open(url)
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        print_env_variable(token)
    else:
        print_env_variable(token)

if __name__ == '__main__':
    main()