
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
        'MOVE': {  # offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [7.3, 2.09], 'OFFSET': [6.5, 3.5]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [2], 'OFFSET': [14, 6]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [19.5, 1.33], 'OFFSET': [15]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [19.5, 1.275], 'OFFSET': [15]}
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
    },
    4: {
        'MOVE': {  # offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [6.3, 2.09], 'OFFSET': [11, 5.3]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [2], 'OFFSET': [16, 6]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [18.5, 1.33], 'OFFSET': [16.5]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [16.5, 1.275], 'OFFSET': [16.5]}
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
    },
    5: {
        'MOVE': {  # offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [7.3, 2.09], 'OFFSET': [11, 6]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [2], 'OFFSET': [16, 6]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [19.5, 1.33], 'OFFSET': [17]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [19.5, 1.275], 'OFFSET': [17]}
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
    },
    6: {
        'MOVE': {  # offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [7, 3], 'OFFSET': [11, 6]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [1], 'OFFSET': [16, 6]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [20.1, 1], 'OFFSET': [17]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [20.3, 2.3], 'OFFSET': [17]}
            #  [76, 2.22]
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.358, 0.196]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.344, 0.16]}
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
    },
    7: {
        'MOVE': {  # offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [7.3, 2.09], 'OFFSET': [11, 6]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [2], 'OFFSET': [16, 6]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [19.5, 1.33], 'OFFSET': [17]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [19.5, 1.275], 'OFFSET': [17]}
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
TREATING_ZONE = 23


def getMotion(roboID):
    return MOTION[roboID]


def getBody():
    return BODY


def getRadius():
    return BALL_RADIUS
