# CONCEPT 4: ABSTRACTION
# User only knows WHAT to do, not HOW it works.

class CoffeeMachine:

    def make_coffee(self):
        self._heat_water()
        self._grind_beans()
        self._brew_coffee()
        print("☕ Coffee Ready!")

    def _heat_water(self):
        print("Heating water...")

    def _grind_beans(self):
        print("Grinding beans...")

    def _brew_coffee(self):
        print("Brewing coffee...")

machine = CoffeeMachine()

machine.make_coffee()