import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

import requests
from commons.config import CommonBaseConfig
from commons.enums import SSOGroups
from jose import jwt
from jose.constants import ALGORITHMS

CLIENTS = {
    "at_course": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJYdWp4bjZma1J2NFREZ0g5X0dPTk5RS2tGeTRDRUQwTXRNcktRNGlrdm4wIn0.eyJleHAiOjE2Mjc5Nzk3MTksImlhdCI6MTYyNzk3ODgxOSwianRpIjoiNDc4MmY4YzEtNjQ5Yi00NGFkLTkyOGMtZmNmYTUyYzc0MmRmIiwiaXNzIjoiaHR0cHM6Ly9zc28tc3RnLnNhZmNzcC5jbG91ZC9hdXRoL3JlYWxtcy9tYWluIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImU5YjQyZTEyLWM1NzgtNGU1Yi1iMDA1LTYxY2Q1MDkwZGM1NCIsInR5cCI6IkJlYXJlciIsImF6cCI6ImF0X2NvdXJzZSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9zdGctYXBpLnNhZmNzcC5jbG91ZCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJhZG1pbiIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgZW1haWwgcHJvZmlsZSIsImNsaWVudEhvc3QiOiIzNy4yMjQuNTIuMTgiLCJjbGllbnRJZCI6ImF0X2NvdXJzZSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LWF0X2NvdXJzZSIsImNsaWVudEFkZHJlc3MiOiIzNy4yMjQuNTIuMTgiLCJwcm9maWxlX2NvbXBsZXRlIjp0cnVlfQ.g2iP9zRZARwAz-iyvRYvV2A0bTQ-gSdxmHeS7-XLoe0ZzoREb5_pncksxWQpnl6NxAGILqk_luLMIBjU650t5kU35xSpk6znJnDqvkHAUTrh0CIwM1bsa282dBaphlmHEOaB6jT7E1aKv6jiDaYIvc3qklL2ofr14OUsNYY2FyM_kNR6dlrGNv8Gnd3ozWxkXkslbS7_D5Yu-qlVRVDjvW60xTroOASeB5-_Z7QGU6-_qucxju1_fRrL3b3kj4OaCxZNMVhN57e0gKluDGdhoDXaKV4VMTAJReXeiyVG8JQuA19nvKsWAUwOkY_5za5ES-mDMi_WT6xfL8kT-j7vrQ",  # noqa
    "coders_hub": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJYdWp4bjZma1J2NFREZ0g5X0dPTk5RS2tGeTRDRUQwTXRNcktRNGlrdm4wIn0.eyJleHAiOjE2Mjc5Nzk3NjksImlhdCI6MTYyNzk3ODg2OSwianRpIjoiZjEyNThiNGYtOTdiYS00NGM2LTlkZjItZjJiMDhhYWIyNTM4IiwiaXNzIjoiaHR0cHM6Ly9zc28tc3RnLnNhZmNzcC5jbG91ZC9hdXRoL3JlYWxtcy9tYWluIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6IjQ5ZjIxODVlLWVhODgtNGJiNy04MmVjLTYwMDkzMjc1MzdjZSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImNvZGVyaHViLWFwaSIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9zdGctYXBpLnNhZmNzcC5jbG91ZCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJjbGllbnRJZCI6ImNvZGVyaHViLWFwaSIsImNsaWVudEhvc3QiOiIzNy4yMjQuNTIuMTgiLCJlbWFpbF92ZXJpZmllZCI6ZmFsc2UsInByZWZlcnJlZF91c2VybmFtZSI6InNlcnZpY2UtYWNjb3VudC1jb2Rlcmh1Yi1hcGkiLCJjbGllbnRBZGRyZXNzIjoiMzcuMjI0LjUyLjE4IiwicHJvZmlsZV9jb21wbGV0ZSI6dHJ1ZX0.GimSXFxxcljQTzL9BpFnBXbVm-xgc9iHL-FDbalcl30wvdZww8irGFIVuDVTq-2GmatSiyZiBbyApc7cAg1gv_r-MFM4KBAe6hGnRcy-mnbpB0KMfh-eooMg_WIp6Q2VRx2wF0-Ld1LlRI2ksSu7iBWktZdRri1KHNiYT-jackkbzUr1dqjBnMDXas5JmxIPcei64oIsBzRYWqZcwV5wwkFKSdjPeqeMkPKxugKDl3IgHX5LB9Up3WRyk3B52Uu1ffGRD-zaoosDk4bdJ2Ro0umSg_kztEUpkh-S9kAOsitC_Oiu8m7tOX3fF090__5lL5lxDDUxurjH4YP3k2gJBA",  # noqa
    "bootcamps": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJYdWp4bjZma1J2NFREZ0g5X0dPTk5RS2tGeTRDRUQwTXRNcktRNGlrdm4wIn0.eyJleHAiOjE2MjgxNjc5MTgsImlhdCI6MTYyODE2NzAxOCwianRpIjoiOTU2NGJjYmEtZDg3OS00YThkLWE1N2EtOWIyZTRiMjU1N2NhIiwiaXNzIjoiaHR0cHM6Ly9zc28tc3RnLnNhZmNzcC5jbG91ZC9hdXRoL3JlYWxtcy9tYWluIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImQxOTU1ZDI5LWNkZjMtNDM4OS05NzU5LTFkNDI2ZDBlOTFhZSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImJvb3RjYW1wcy1hcGkiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJib290Y2FtcHMtYXBpIjp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwiY2xpZW50SWQiOiJib290Y2FtcHMtYXBpIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJjbGllbnRIb3N0IjoiMzcuMjI0LjUyLjE4IiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LWJvb3RjYW1wcy1hcGkiLCJjbGllbnRBZGRyZXNzIjoiMzcuMjI0LjUyLjE4IiwicHJvZmlsZV9jb21wbGV0ZSI6dHJ1ZX0.ME246Oi3lq-wkpM9qpvQ912JJwqgD8FYl1Xcwzuji3TP9YZC0nMqh9IQ53SN50SRBvQ2jQRzWwZ9xnslTmBN1J-l2LbzNveQp5kNxypxT6SWC60DJRIBwcmTxbyW4v09KGDuv7UO38eMUElG8NxF2pknWgWKbZAl4TSQ65rMzU1jmeqa8gOiGmG3yMlmWuJ7Dyu7fZluweox9ggPu6t4o8X6nsYRjgLMU-4shpxLb46je-kE-itmiLdkMMyd5Q51lbE4d3k5jcnUDpFHsN-NkoGbiHYu8L780blCcoJI48JTnNdknHFJnVqfueHjo_6XWxH60f02JSznNYQZUin1HQ",  # noqa
    "hiring": "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJYdWp4bjZma1J2NFREZ0g5X0dPTk5RS2tGeTRDRUQwTXRNcktRNGlrdm4wIn0.eyJleHAiOjE2MjgxNjc5MTgsImlhdCI6MTYyODE2NzAxOCwianRpIjoiOTU2NGJjYmEtZDg3OS00YThkLWE1N2EtOWIyZTRiMjU1N2NhIiwiaXNzIjoiaHR0cHM6Ly9zc28tc3RnLnNhZmNzcC5jbG91ZC9hdXRoL3JlYWxtcy9tYWluIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImQxOTU1ZDI5LWNkZjMtNDM4OS05NzU5LTFkNDI2ZDBlOTFhZSIsInR5cCI6IkJlYXJlciIsImF6cCI6ImJvb3RjYW1wcy1hcGkiLCJhY3IiOiIxIiwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iXX0sInJlc291cmNlX2FjY2VzcyI6eyJib290Y2FtcHMtYXBpIjp7InJvbGVzIjpbInVtYV9wcm90ZWN0aW9uIl19LCJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwiY2xpZW50SWQiOiJib290Y2FtcHMtYXBpIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJjbGllbnRIb3N0IjoiMzcuMjI0LjUyLjE4IiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LWJvb3RjYW1wcy1hcGkiLCJjbGllbnRBZGRyZXNzIjoiMzcuMjI0LjUyLjE4IiwicHJvZmlsZV9jb21wbGV0ZSI6dHJ1ZX0.ME246Oi3lq-wkpM9qpvQ912JJwqgD8FYl1Xcwzuji3TP9YZC0nMqh9IQ53SN50SRBvQ2jQRzWwZ9xnslTmBN1J-l2LbzNveQp5kNxypxT6SWC60DJRIBwcmTxbyW4v09KGDuv7UO38eMUElG8NxF2pknWgWKbZAl4TSQ65rMzU1jmeqa8gOiGmG3yMlmWuJ7Dyu7fZluweox9ggPu6t4o8X6nsYRjgLMU-4shpxLb46je-kE-itmiLdkMMyd5Q51lbE4d3k5jcnUDpFHsN-NkoGbiHYu8L780blCcoJI48JTnNdknHFJnVqfueHjo_6XWxH60f02JSznNYQZUin1HQ",  # noqa
}

TOKENS = {
    "hiring_admin": [SSOGroups.HIRING_ADMINS.value],
    "test_instructor": [SSOGroups.INSTRUCTORS.value],
    "test_teacher": [SSOGroups.LMS_TEACHERS.value],
    "test_teacher2": [SSOGroups.LMS_TEACHERS.value],
    "sender_admin": [SSOGroups.SMS_SENDERS.value],
    "hiring_user_1": [SSOGroups.HIRING_ORG.value],
    "hiring_user_2": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_1": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_2": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_3": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_4": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_5": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_6": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_7": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_8": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_9": [SSOGroups.HIRING_ORG.value],
    "test_hiring_user_10": [SSOGroups.HIRING_ORG.value],
    "student_tester1": [SSOGroups.FORMS_WORKSPACE_USERS.value],
    "student_tester2": [],
    "test_user_1": [],
    "test_user_2": [],
    "test_user_3": [],
    "test_user_4": [],
    "test_user_5": [],
    "test_user_6": [],
    "test_user_7": [],
    "test_user_8": [],
    "test_user_9": [],
    "test_user_10": [],
    "admin_tester": [
        SSOGroups.BOOTCAMP_ADMINS.value,
        SSOGroups.LMS_ADMINS.value,
        SSOGroups.SATR_ADMINS.value,
        SSOGroups.SMS_SENDERS.value,
        SSOGroups.GUEST_FLIGHT_ADMIN.value,
        SSOGroups.CODERHUB_ADMINS.value,
    ],
}


@lru_cache
def get_tokens():
    path = Path(__file__).parent / "./test_tokens.json"
    with path.open(mode="r", encoding="utf8") as file:
        test_tokens = json.load(file)
    return test_tokens


def get_token(username: str):
    test_tokens = get_tokens()

    return test_tokens[username]


def get_token_by_client(client_name: str, config: CommonBaseConfig):
    return CLIENTS[client_name]


def upload_asset(upload_url: str):
    with open("../commons/testing/test_asset.png", "rb") as f:
        response = requests.put(upload_url, data=f)
    assert response.status_code == 200


def update_user_token(user_token, roles):
    token = user_token["Authorization"][7 : len(user_token["Authorization"])]
    decoded_token = jwt.decode(
        token,
        key="",
        options={
            "verify_signature": False,
            "verify_exp": False,
            "verify_aud": False,
        },
        algorithms="RS256",
    )
    for role in roles:
        decoded_token["realm_access"]["roles"].append(role)

    new_token = jwt.encode(
        decoded_token,
        key="MUST",
        algorithm=ALGORITHMS.HS256,
    )
    new_user_token = deepcopy(user_token)

    new_user_token["Authorization"] = f"Bearer {new_token}"
    return new_user_token
