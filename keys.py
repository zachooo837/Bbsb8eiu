from datetime import datetime
from random import randrange
import random
import string
# KEY FORMAT  key-da13-dksa-kkks

now = datetime.now()

# FOUR PARTS, DATE-RANDOM-RANDOM-UID-
def gen(days = 1):
    # DATE
    f = str(randrange(3712,99999))
    k = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
    key = "drift" + "-"  + k + "-" + str(f) + "-" + str(days) 
    return key

def birthdate():
    return now.strftime('%m/%d/%Y-%H:%M:%S')

