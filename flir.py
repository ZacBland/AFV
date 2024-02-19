from flirpy.camera.lepton import Lepton

camera = Lepton()
image = camera.grab()
camera.close()