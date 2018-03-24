import requests

headers = {
    "host": "api.ncuos.com", 

    "Accept-Encoding": "gizp",
    "Authorization": "passport eyJhbGciOiJIUzI1NiIsImV4cCI6MTUyMTg1MjIwNywiaWF0IjoxNTIxODQ5MjA3fQ.eyJ4aCI6IjU2MDIyMTYwMzMiLCJpZCI6IjU3MzQ2NjcwMjkiLCJleHAiOjE1MjE4NTIyMDd9.PSVzcoXd8K7NfY2KmdmrcCPuaGoW0P7jBL0XShtZwlE",

    "Accept": "application/json, text/plain, */*"}

r = requests.get("http://120.27.137.151/api/info/scores", headers=headers)

print(r.text)