

from apis.Users import data


username_table = {u.name:u for u in data}
userid_table = {u.id:u for u in data}

def authenticate(name,password):
    user = username_table.get(name,None)
    if user and password == user.password:
        return user
    
def identity(payload):
    id = payload['identity']
    return userid_table.get(id,None)

