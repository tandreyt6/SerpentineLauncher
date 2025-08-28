from pypresence import Presence

CLIENT_ID = "1410672904773042349"
rpc = Presence(CLIENT_ID)
try:
    rpc.connect()

    rpc.update(large_image="logo")

    def set_status(state="", details=""):
        print("[DISCORD] update status: ", state, details)
        rpc.update(state=state, details=details)
except:
    def set_status(state="", details=""):
        pass