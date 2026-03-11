import random

class Lottery:
    def buy_ticket(self):
        if random.randint(1, 10000000) == 42:
            return "You won a million kopecks!"
        else:
            return "Maybe next time"


def buy_ticket_test():
    lottery = Lottery()
    result = lottery.buy_ticket()
    assert result == "You won a million kopecks!"