
########## Robot #################
cm_px = 2.33
BODY = {
    'width': 17,  # cm full length
    'length': 11,  # cm foot length   
    'depth': 0,
    'diagonal': 0,
    'feet_apart': 5  # distance from one feet to center when kicking
}
MOTION = {
    1: {
        'MOVE': {  # offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [5, 1], 'OFFSET': [11.25, 6, 8.75]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [1], 'OFFSET': [10.25, 6]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [20, 0.65], 'OFFSET': [13.5]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [18, 0.8], 'OFFSET': [13.5]}
            #  [76, 2.22]
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.4, 0.19]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.4, 0.19]}
        },

        'KICK': {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': [3.25, 3]},  # 5.5 12  # [kick way, another]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': [5.75, 3]},  # 5.5- 17
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': [4.5, 5.5]},  # 9-18
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': [4.75, 3]}
        },
        'DEFENCE': {
            'FORE': {'CMD': ['Y']},
            'LEFT': {'CMD': ['f']},
            'RIGHT': {'CMD': ['g']}
        },
        'REST': {'CMD': ['r']}
    },
    3: {
        'MOVE': {  # offset[verticle(, horizon)]
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [8, 1], 'OFFSET': [11.25, 5, 8.75]},  # the third is for pass
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [1], 'OFFSET': [11.25, 5]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [19, 0.8], 'OFFSET': [13]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [18, 1.3], 'OFFSET': [13]}
            #  [76, 2.22]
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.4, 0.112]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.4, 0.136]}
        },

        'KICK': {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': [3.25, 3]},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': [5.75, 3]},
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': [5.5, 5.5]},
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': [5.75, 3]}
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
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [7, 1.0], 'OFFSET': [11.25, 5.5, 8.75]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [1.5], 'OFFSET': [10.25, 6]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [17, 1.7], 'OFFSET': [13]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [15, 2.7], 'OFFSET': [13]}
            #  [76, 2.22]
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.4, 0.125]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.4, 0.11]}
        },

        'KICK': {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': [3.25, 3]},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': [5.75, 3]},
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': [4, 5.5]},
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': [4.75, 3]}
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
            'PASS': {'CMD': ['o', 'p'], 'BOUND': [3.25, 3.25]},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': [3.25, 3.25]},
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
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [10, 1], 'OFFSET': [11.25, 5, 8.75]},  # 5.5
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [1], 'OFFSET': [11.25, 5]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [17, 1], 'OFFSET': [13]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [19, 0.8], 'OFFSET': [13]}
            #  [76, 2.22]
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.4, 0.116]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.4, 0.108]}
        },

        'KICK': {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': [3.25, 3.25]},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': [5.75, 3.25]},
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': [6, 5.5]},
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': [5.75, 3.25]}
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
            'FORE': {'CMD': ['W', 'w'], 'BOUND': [9, 1.8], 'OFFSET': [11.25, 5.5, 8.75]},
            # BOUND': [30, 15] for simulator [18, 8]
            'BACK': {'CMD': ['s'], 'BOUND': [4.5], 'OFFSET': [10.25, 5.5]},
            # BOUND': [15] ;[4]
            'LEFT': {'CMD': ['A', 'a'], 'BOUND': [20, 3.5], 'OFFSET': [14.25]},
            # BOUND': [75,15] ;[71, 3.1]
            'RIGHT': {'CMD': ['D', 'd'], 'BOUND': [20, 4.4], 'OFFSET': [14.25]}
            #  [76, 2.22]
        },

        'TURN': {
            'LEFT': {'CMD': ['Q', 'q'], 'BOUND': [0.5, 0.14]},
            'RIGHT': {'CMD': ['E', 'e'], 'BOUND': [0.45, 0.13]}
        },

        'KICK': {
            'PASS': {'CMD': ['o', 'p'], 'BOUND': [3.25, 3]},  # [left, right]
            'FSHOOT': {'CMD': ['u', 'i'], 'BOUND': [5.75, 3]},
            'SSHOOT': {'CMD': ['h', 'j'], 'BOUND': [5.75, 5.5]},
            'BSHOOT': {'CMD': ['b', 'n'], 'BOUND': [4.75, 3]}
        },
        'DEFENCE': {
            'FORE': {'CMD': ['y']},
            'LEFT': {'CMD': ['f']},
            'RIGHT': {'CMD': ['g']}
        },
        'REST': {'CMD': ['r']}
    }
}

BALL_RADIUS = 3.75  # Ball Size #diameter 6.5cm = 20 pixel
DANGER_SPEED = 9
TREATING_ZONE = 23


def getMotion(roboID):
    return MOTION[roboID]


def getBody():
    return BODY


def getRadius():
    return BALL_RADIUS
