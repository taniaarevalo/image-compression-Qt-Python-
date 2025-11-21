"""
NOM: Arévalo
PRÉNOM: Tania
SECTION: B1-INFO
MATRICULE: 00570504"""

from pixel import Pixel
class Image:
    def __init__(self, width:int, height:int, pixels:list[Pixel]):
        self.width = self.verification_de_entier(width)
        self.height = self.verification_de_entier(height)
        self.pixels = self.verification_de_liste(pixels)
        
    def verification_de_entier(self, valeur):
        if not isinstance(valeur, int):
            raise Exception("Ce n'est pas un entier.")
        return valeur

    def verification_de_liste(self, liste):
        if not isinstance(liste, list):
            raise Exception("Ce n'est pas une liste.")
        if len(liste) > self.width * self.height:
            raise Exception("Le nombre de pixels n'est pas correct.", len(liste))
        if len(liste) < self.width * self.height:
            raise Exception("Le nombre de pixels n'est pas correct.")
        for p in liste:
            if isinstance(p, tuple):
                raise Exception("Il y a 1/des instances incorrectes dans la liste de pixels.")
        return liste

    def __getitem__(self, pos: tuple[int, int]):
        """La position du pixel est calculée avec deux "aires rectangulaires", c'est-à-dire, 1) je calcule tous les pixels se trouvant avant celui qui est recherché, sans compter ceux qui se trouvent sur sa ligne (aire 1), 2) je calcule le nombre de pixels sur la ligne du pixel recherché, avant celui-ci. (aire2)
            Ensuite, """
        if isinstance(pos, tuple):
            if pos[0] < 0 or pos[0] > (self.width - 1):
                raise IndexError("La position n'existe pas.")
            if pos[1] < 0 or pos[1] > (self.height - 1):
                raise IndexError("La position n'existe pas.")
            pixels_h_apres = self.height - pos[1] # Compte le nombre de "lignes" de pixels après le pixel recherché + celle où se trouve le pixel.
            pixels_h_avant = self.height - pixels_h_apres # Compte le nombre de "lignes" de pixels avant le pixel recherché. (aire 1)
            cases_pixels_h = self.width*pixels_h_avant
            case = cases_pixels_h + pos[0]
        elif isinstance(pos, int):
            case = pos
        return self.pixels[case]
    
    def __setitem__(self, pos: tuple[int, int], pix: Pixel):
        if pos[0] < 0 or pos[0] > (self.width - 1):
            raise IndexError("La position n'existe pas.")
        if pos[1] < 0 or pos[1] > (self.height - 1):
            raise IndexError("La position n'existe pas.")
        pixels_h_apres = int(self.height) - pos[1] # Compte le nombre de "lignes" de pixels après le pixel recherché + celle où se trouve le pixel.
        pixels_h_avant = int(self.height) - int(pixels_h_apres) # Compte le nombre de "lignes" de pixels avant le pixel recherché. (aire 1)
        cases_pixels_h = int(self.width*pixels_h_avant)
        self.pixels[cases_pixels_h + pos[0]] = pix
        
    def __eq__(self, other: 'Image'):
        res = False
        if (self.width == other.width) and (self.height == other.height) and (self.pixels == other.pixels):
            res = True
        return res
