class Messages():
    @property
    def bootup(self):
        return "ALTTP Racebot is booting up"

    @property
    def login_successful(self):
        return "Login successful"

    @property
    def alreadystarted(self):
        return "My dude :( a race is already started!"

    @property
    def startrace(self):
        return "A race! Nice my dude, type .join to participate!"

    @property
    def stoprace(self):
        return "Ooh no my dude :( the race is no more"

    @property
    def norace(self):
        return "Duuuude, no race is running.. better got up on that"

    def joinrace(self, name):
        return "Welcome my dude {}!".format(name)

    def quitrace(self, name):
        return "Sad to see you go my dude {}!".format(name)

    @property
    def countdown(self):
        return "Aww yeah! Lets get this party started! Counting down from 10.."

    @property
    def go(self):
        return "GO GO GO"
    
    def remaining(self, num):
        return "My dude, we're so pumped! Waiting for {} players".format(num)

    @property
    def alreadydone(self):
        return "But dude, you're already finished?!"

    def done(self, time):
        return "Dude, {}! SICK, gg wp".format(time)

    @property
    def notstarted(self):
        return "Dude, don't jump the gun.. race hasn't even started yet!"

    @property
    def generating_seed(self):
        return "Imma let you finish but there's a seed coming your way soon"
