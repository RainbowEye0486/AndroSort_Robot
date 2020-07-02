
########## Robot #################
cm_px = 3.65
BODY = {
    'width': 17,  # cm full length
    'length': 11,  # cm foot length   
    'depth': 0,
    'diagonal': 0,
    'feet_apart': 5  # distance from one feet to center when kicking
}
MOTION = {
    3: {
        'MOVE': {# offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND':  [7.3, 2.09], 'OFFSET': [11, 6]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [2], 'OFFSET': [16, 6]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [19.5, 1.33], 'OFFSET': [15.5]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [19.5, 1.275], 'OFFSET': [15.5]}
            #  [76, 2.22]
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.358, 0.196]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.358, 0.196]}
        },

        'KICK': {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': []},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': []},
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': []},
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': []}
        },
        'DEFENCE': {
            'FORE': {'CMD': ['Y']},
            'LEFT': {'CMD': ['f']},
            'RIGHT': {'CMD': ['g']}
        },
        'REST': {'CMD': ['r']}
    }
}


BALL_RADIUS = 3.75  # Ball Size #diameter 6.5cm = 20 pixel
DANGER_SPEED = 30
TREATING_ZONE = 30

def getMotion(roboID):
    return MOTION[roboID]


def getBody():
    return BODY


def getRadius():
    return BALL_RADIUS
