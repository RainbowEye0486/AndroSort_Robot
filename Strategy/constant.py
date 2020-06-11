
########## Robot #################

BODY = {
    'width': 25,
    'depth': 0,
    'diagonal': 0,
    'feet_apart': 5 # distance from one feet to center when kicking
}
MOTION = {
    3: {
        'MOVE': {
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [18, 8]},
            'BACK': {'CMD': ['s'], 'BOUND': [4]},
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [71, 3.1]},
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [76, 2.22]}
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.6, 0.3]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.6, 0.3]}
        },

        'KICK': {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': []},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': []},
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': []},
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': []}
        },
        'DEFENCE': {
            'FORE':{'CMD': 'Y'},
            'LEFT':{'CMD': 'f'},
            'RIGHT':{'CMD': 'g'}
        },
        'REST': {'CMD': 'r'}
    }
}


BALL_RADIUS = 10  # Ball Size #diameter 6.5cm = 20 pixel


def getMotion(roboID):
    return MOTION[roboID]


def getBody():
    return BODY


def getRadius():
    return BALL_RADIUS
