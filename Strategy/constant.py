
########## Robot #################
cm_px = 3.7
BODY = {
    'width': 17,  # cm full length
    'length': 11,  # cm foot length   
    'depth': 0,
    'diagonal': 0,
    'feet_apart': 5 # distance from one feet to center when kicking
}
MOTION = {
    3: {
        'MOVE': {# offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND':  [30/cm_px, 15/cm_px], 'OFFSET': [5.5, 3]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [15/cm_px], 'OFFSET': [5.5, 3]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [75/cm_px, 15/cm_px], 'OFFSET': [9.5]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [75/cm_px, 15/cm_px], 'OFFSET': [9.5]}
            #  [76, 2.22]
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.9, 0.45]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.9, 0.45]}
        },

        'KICK': {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': []},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': []},
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': []},
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': []}
        },
        'REST': {'CMD': ['r']}
    }
}


BALL_RADIUS = 2.7  # Ball Size #diameter 6.5cm = 20 pixel


def getMotion(roboID):
    return MOTION[roboID]


def getBody():
    return BODY


def getRadius():
    return BALL_RADIUS
