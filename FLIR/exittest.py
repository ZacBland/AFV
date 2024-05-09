import atexit

def exit():
    print("Test")



atexit.register(exit)

while True:
    pass