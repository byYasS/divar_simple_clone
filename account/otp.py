from .services.sms import send_sms
import random
import redis


r = redis.Redis("localhost", 6379, decode_responses=True)

def get_or_create_otp(phone):
    if r.get(f"otp:{phone}"):
        pass
    else:
        otp = random.randint(100000, 999999)    
        r.setex(f"otp:{phone}", 120, otp)
        send_sms(phone, otp)
        
        
def is_otp_valid(phone, otp):
    if r.get(f"otp:{phone}") == otp:
        return True
    
    
def get_otp_ttl(phone):
    ttl = max(r.ttl(f"otp:{phone}"), 0)
    return ttl

       
def resend_otp(phone):
    new_otp = random.randint(100000, 999999)    
    r.setex(f"otp:{phone}", 120, new_otp)
    send_sms(phone, new_otp)
    
    
def delete_otp(phone):
    r.delete(f"otp:{phone}")