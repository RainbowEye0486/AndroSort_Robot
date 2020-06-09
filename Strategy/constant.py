

########## Robot #################

BODY = {
    'width':25,
    'depth': 0,
    'diagonal':0
}
MOTION = {
    3: {
        MOVE = {
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [18, 8]},
            'BACK': {'CMD': ['s'], 'BOUND': [4]},
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [71, 3.1]},
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [76, 2.22]}
        }

        TURN = {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [18, 8]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [18, 8]}
        }

        KICK = {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': []},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': []},
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': []},
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': []}
        }
    }
}


def getMotion(roboID):
    return MOTION[roboID]