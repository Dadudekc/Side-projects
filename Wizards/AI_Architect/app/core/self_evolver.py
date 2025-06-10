class SelfEvolver:
    def __init__(self, initial_state):
        self.state = initial_state

    def evolve(self):
        self.state += 1
        return self.state

if __name__ == "__main__":
    evolver = SelfEvolver(0)
    print(evolver.evolve())
