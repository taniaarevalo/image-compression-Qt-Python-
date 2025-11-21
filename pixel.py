"""
NOM: Arévalo
PRÉNOM: Tania
SECTION: B1-INFO
MATRICULE: 00570504"""

class Pixel:  
    """ 
    S'occupe des possibles erreurs, l'initialisation du constructeur et plus. 
    """

    def __init__(self, rouge, vert, bleu):  # Les trois valeurs sont envoyées pour un check up de erreurs.
        self.rouge = self.valeur_de_un_entier(rouge)
        self.vert = self.valeur_de_un_entier(vert)
        self.bleu = self.valeur_de_un_entier(bleu)

    def valeur_de_un_entier(self, valeur):  # Fonction regarde si la valeur est un entier, si c'est une valeur entre 0 et 255.
        if not isinstance(valeur, int):
            raise TypeError("Ce n'est pas un entier.")
        if valeur < 0:
            raise ValueError("Ce nombre est inférieur à 0.", valeur)
        if valeur > 255:
            raise ValueError("Ce nombre est supérieur à 255.")
        return valeur

    def __eq__(self, other):  # Compare deux Pixels et renvoie un booléen True si ils sont les mêmes.
        res = False
        if isinstance(other, Pixel):
            if (self.rouge == other.rouge) and (self.vert == other.vert) and (self.bleu == other.bleu):
                res = True
        return res
        
    def get_rouge(self):  # Retourne la saturation du rouge.
        return self.rouge

    def get_vert(self):  # Retourne la saturation du vert.
        # Peut-être pour après, les getters, car dans l'énoncé il est écrit qu'il faut récupérer, mais pas modifier,
        # pas de setters.
        return self.vert

    def get_bleu(self):  # retourne la saturation du bleu.
        # Peut-être pour après, les getters, car dans l'énoncé il est écrit qu'il faut récupérer, mais pas modifier,
        # pas de setters.
        return self.bleu


