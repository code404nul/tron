import msvcrt
class Inputbinding():
    def __init__(self,tab):
        self.up=tab[0]
        self.down=tab[1]
        self.left=tab[2]
        self.right=tab[3]

    def __str__(self):
        return ""





while True:
    print(ord(msvcrt.getwch()))
