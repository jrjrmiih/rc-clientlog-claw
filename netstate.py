from transitions import Machine


class NetState:
    states = [
        'unknown',
        'none',
        '4g',
        '3g',
        '2g'
    ]

    def __init__(self):
        self.machine = Machine(model=self, states=NetState.states, send_event=True)
