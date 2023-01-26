import json

with open("json_data/users.json") as file:
    data = file.read()

print(data)

users = json.loads(data)

print(users)