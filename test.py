class PLayer:
    def __init__(self):
        self.toto = 0
        self.tata = 4
    def test(self):
        print("aie")
        
class Player_Ai(PLayer):
    def __init__(self):
        super().__init__()
        
jouer1=Player_Ai()
jouer1.test()