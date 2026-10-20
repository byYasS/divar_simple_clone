import redis


r = redis.Redis("localhost", 6379, 1, decode_responses=True)


def add_connection(user_id, connection_id):
    key = f"presence:user:{user_id}"
    
    r.sadd(key, connection_id)
    
    
def remove_connection(user_id, connection_id):
    key = f"presence:user:{user_id}"
    
    r.srem(key, connection_id)
    
    connections = r.scard(key)
    
    if connections == 0:
        r.delete(key)

  
def is_online(user_id):
    key = f"presence:user:{user_id}"
    
    return r.scard(key) > 0