"""
NOM: Arévalo
PRÉNOM: Tania
SECTION: B1-INFO
MATRICULE: 00570504
"""


from pixel import Pixel
from image import Image
from messageserror import MainWindow

class Encoder:

    def __init__(self, img: Image, version: int = 1, **kwargs):
        """
        Constructeur contiendra les paramètres à des variables. Et il cherchera d'éventuelles erreurs dans celles-ci.
        """

        self.image = img  # Assignation de la classe Image dans self.image.
        self.version = version  # Assignation de la version dans self.version.
        self.possibles_versions = [1, 2, 3, 4]  # 4 versions possibles (entiers).
        self.possible_depths = [1, 2, 4, 8, 24]  # 5 profondeurs possibles (entiers).
        self.possible_keys = ['depth', 'rle']  # 2 noms possibles (str).

        if self.version not in self.possibles_versions:
            raise ValueError("Vous n'avez pas choisi une bonne version.")

        if self.version == 3:  # Il y a des erreurs supplémentaires qui peuvent être faites dans la version 3.
            for key in kwargs.keys():  # Noms de l'élément reçu dans le dictionnaire kwargs sont incorrects.
                if key not in self.possible_keys:
                    raise KeyError("Le nom est incorrect.")
            
            self.depth = kwargs['depth']
            self.rle = kwargs['rle']

            if self.depth not in self.possible_depths:  # Si la valeur de la clé "depth" est incorrecte.
                raise ValueError("La profondeur n'est pas correcte.")
            if type(self.rle) is not bool:  # Si clé "rle" ne contient pas un booléen.
                raise ValueError("Rle n'est pas un booléen.")
            if (self.rle is False and self.depth > 4) or (self.rle is True and self.depth < 8):  # Si la profondeur et la rle ne sont pas liées (rle True que pour depth 8 et 24).
                raise ValueError("La rle ou la profondeur n'est pas correcte.")
            
            if kwargs["rle"] == False:  # Si le booléen de rle est False, la valeur contenue dans self.rle sera 0, sinon elle sera 1.
                self.rle = 0
            else:
                self.rle = 1
        
        self.image_bytes = bytearray()  # initialisation de bytearray()
        self.palette = {}  # initialisation de la palette

    
    def header_bytearray(self):
        """
        Fonction initialise le début de la bytearray() (header) qui est similaire dans chaque version, il faudra recevoir comme paramètres: version, width et height.
        """

        for lettre in 'ULBMP':  # Chaque lettre est placée dans la bytearray, elle est d'abord transformée en entier représentant le caractère unicode, qui est à sont tour transformé en un byte.
            self.image_bytes += ord(lettre).to_bytes(1, byteorder='little')

        self.image_bytes += self.version.to_bytes(1, byteorder='little') # Rajout de la version de la même façon.
        
        if self.version == 1 or self.version == 2 or self.version == 4:  # Pour les deux premières, ainsi que pour la dernière, c'est un header de 12.
            self.image_bytes += (12).to_bytes(2, byteorder='little')  # Header est placée en 2 bytes, pour les futures versions, où le header pourrait être supérieur à 255.
        
        elif self.version == 3:  # Dans la version 3 le header dépend de la taille de la palette, mais il est initialisé à 20, et changé par la suite.
            self.image_bytes += (14).to_bytes(2, byteorder='little') # peut changer: sinon 13 + len(palette) (24: 14)
        
        # Ensuite, la largeur et hauteur de l'image sont ajoutées (aussi en 2 bytes).
        self.image_bytes += self.image.width.to_bytes(2, byteorder='little')
        self.image_bytes += self.image.height.to_bytes(2, byteorder='little') 
    

    def pixels_encodage(self, repetitions, rouge, vert, bleu):  
        """
        Fonction qui va enregistrer les pixels dans la bytearray().
        """

        self.image_bytes += repetitions.to_bytes(1, byteorder='little')  # Premièrement, le nombre de répétitions est ajouté.
        self.image_bytes.extend([rouge, vert, bleu])  # Ensuite, les trois bytes du Pixel.
    

    def palette_mapping(self):
        """
        Fonction pour créer la palette et l'insérer dans la bytearray(). Cette fonction va modifier la bytearray et changer le header.
        """

        indice = 0   # Indice pour gérer ces éléments. Sera aussi la key.
        
        # !!! Les différentes couleurs sont placées dans leur ordre de découverte dans la liste de pixels. !!!
        for pix in self.image.pixels:  # Dans le dictionnaire, les couleurs sont rajoutés une à une. {key(indice): value(Pixel(R, G, B))}
            if pix not in self.palette.values():  # Si la couleur n'a pas encore était rajoutée, elle est rajoutée.
                self.palette[indice] = Pixel(pix.rouge, pix.vert, pix.bleu)  # Pixel est une valeur de dictionnaire.
                indice += 1  # Incrémentation pour passer au prochain élément de la palette.
        
        # Placer les différentes valeurs de la palette dans la bytearray().
        for val in self.palette.values():
            self.image_bytes.extend([val.rouge, val.vert, val.bleu])

        self.image_bytes[6:8] = (14 + len(self.palette)*3).to_bytes(2, byteorder='little')
        

    def encodage_partiel(self):
        """
        Pour ne pas avoir de répétitions dans la version 2 et 3 (self.depth = 8 et 24), à cause de la RLE. """
        
        compteur, initial, suivant = 1, 0, 1  # compteur, initial et suivant sont à nouveau initialisés.
                
        while suivant < len(self.image.pixels):  # Tant que le dernier pixel n'a pas été parcouru, il faut observer les pixels et compter si certains se répétent et sont consécutifs.
                    
            if Pixel.__eq__(self.image.pixels[initial], self.image.pixels[suivant]) is True:  # Si les deux pixels comparés sont les mêmes.
                        
                if suivant != len(self.image.pixels) - 1:  # Liste n'est pas encore finie, variables sont incrémentées.
                            
                    compteur += 1
                    initial += 1
                    suivant += 1
                        
                else:  # La liste est finie.

                    while compteur > 0:  # Tant que le compteur n'est pas égal  à 0, alors il faut enregistrer ces pixels une fois. Re-initialisation du compteur en 0 car il pourrait être réutilisé.
                                
                        if compteur < 255:  # Si le compteur est plus petit que 255, encoder le compteur et le pixel tout de suite.
                            
                            self.pixels_encodage(compteur+1, self.image.pixels[initial].rouge, self.image.pixels[initial].vert, self.image.pixels[initial].bleu)
                                
                            compteur = 0  # Puis, réinitialisation du compteur et incrémentation des valeurs voyageant dans la liste de pixels.
                            initial += 1
                            suivant += 1
                                
                        else:  # Si le compteur est plus grand que 255. Il faut enregistrer les pixels plusieurs fois.
                            
                            self.pixels_encodage(255, self.image.pixels[initial].rouge, self.image.pixels[initial].vert, self.image.pixels[initial].bleu)
                                     
                            compteur -= 255  # Décrémenter 255 au compteur pour diminuer et sortir éventuellement de la boucle + avoir un compteur initialisé à 0.
            
            else:  # Quand deux pixels ne sont pas égaux: enregistrer le(s) pixel(s) précédent(s). Puis continuer le compteur pour le nouveau type de pixel.
                        
                if suivant != len(self.image.pixels) - 1: # Dernier élément final pas encore atteint.
                            
                    if compteur < 255:  # Si le compteur pour l'ancien type de pixel est < 255:
                                
                        if compteur == 0:  # Si le compteur = 0, rien à enregistrer. Preparation des variables au pixel suivant.
                            compteur = 1
                            initial += 1
                            suivant += 1
                        else:  # Si le compteur > 0, enregistrement de l'ancien pixel et reinitialisation des données.
                            
                            self.pixels_encodage(compteur, self.image.pixels[initial].rouge, self.image.pixels[initial].vert, self.image.pixels[initial].bleu)

                            compteur = 1
                            initial += 1
                            suivant += 1
                            
                    else:  # Si le compteur > 255: enregistrer et diminuer le compteur.
                        
                        self.pixels_encodage(self.image_bytes, 255, self.image.pixels[initial].rouge, self.image.pixels[initial].vert, self.image.pixels[initial].bleu)
                            
                        compteur -= 255
                        
                else: # Dernier élément atteint. Enregistrement des deux types de pixels.
                    
                    self.pixels_encodage(compteur, self.image.pixels[initial].rouge, self.image.pixels[initial].vert, self.image.pixels[initial].bleu)
                          
                    compteur = 1

                    self.pixels_encodage(compteur, self.image.pixels[suivant].rouge, self.image.pixels[suivant].vert, self.image.pixels[suivant].bleu)           
                                
                    initial += 1
                    suivant += 1

    def rajout_repetitions(self, indice, compteur):  
        """ 
        Fonction rajoute le compteur contenant les répétitions d'un pixel et ce même pixel dans la bytearray. 
        """

        while compteur > 255:  # Si le compteur est plus grand que 255, il faudra l'enregistrer à plusieurs reprises.
            self.image_bytes += (255).to_bytes(1, byteorder = "little")  # premier compteur sera à 255 ducoup
            self.image_bytes.extend([self.image.pixels[indice].rouge, self.image.pixels[indice].vert, self.image.pixels[indice].bleu])  # rajout de chaque couleur de pixel.
            compteur -= 255  # décrémentation du compteur ajouté.
        self.image_bytes += compteur.to_bytes(1, byteorder = "little")  # une fois qu'il reste le dernier compteur (ou le seul si il était inférieur à 255), il est enregistré.
        self.image_bytes.extend([self.image.pixels[indice].rouge, self.image.pixels[indice].vert, self.image.pixels[indice].bleu])  # ainsi que les couleurs du pixel.
        

    def premier_bloc(self, pixel1, pixel2):
        """
        Fonction s'occupant du premier pixel et celui qui vient avant (le noir), dans la version 4.
        """
        self.image_bytes += (255).to_bytes(1, byteorder = "little")
        self.image_bytes.extend([pixel2.rouge, pixel2.vert, pixel2.bleu])

    def type_bloc(self, pixel1, pixel2):
        """
        Fonction regarde quel type de bloc de pixels utiliser et envoie les informations à la fonction s'occupant de ces blocs.
        """

        # rouge, vert, bleu sont des variables contenant les differences entre pixels
        rouge = pixel2.rouge - pixel1.rouge
        vert = pixel2.vert - pixel1.vert
        bleu = pixel2.bleu - pixel1.bleu

        rouge_vert = rouge - vert   
        bleu_vert = bleu - vert  
        vert_rouge = vert - rouge 
        bleu_rouge = bleu - rouge
        rouge_bleu = rouge - bleu
        vert_bleu = vert - bleu

        # ULBMP_SMALL_DIFF !!!!! Dans ce cas les différentes couleurs des pixels sont très proches numériquement.
        if rouge >= -2 and rouge <= 1: 
            if vert >= -2 and vert <= 1:
                if bleu >= -2 and bleu <= 1:

                    rouge += 2  # Incrémentation de 2 dans ce type de blocs.
                    vert += 2
                    bleu += 2

                    octet = 0  
                    octet = octet | (rouge << 4)  # Les représentation binaire de la différence de couleurs est décalée (rajout de 0 à droite),
                    octet = octet | (vert << 2)  # avec un BITWISE OU nous comparons les résultats avec l'octet modifié.
                    octet = octet | (bleu)

                    self.image_bytes += (octet).to_bytes(1, byteorder = "little")  # Octet rajouté dans la bytearray().
                    return self.image_bytes
        
        # ULBMP_INTERMEDIATE_DIFF !!!!! Ici, les pixels sont aussi proches, l'un de l'autre, mais moins que dans l'ancien cas.
        elif vert >= -32 and vert <= 31:  
            if (rouge_vert >= -8 and rouge_vert <= 7) and (bleu_vert >= -8 and bleu_vert <= 7):

                vert += 32  # rajout de valeurs, pour être certain d'avoir des réponses positives.
                rouge_vert += 8
                bleu_vert += 8

                octet1 = 64  # car il faut rajouter 01 au début
                octet1 = octet1 | vert  # Pour rajouter les bits 1, nous utilisons un BITWISE OU.

                self.image_bytes += octet1.to_bytes(1, byteorder = "little")  # rajout dans la bytearray()

                octet = 0
                octet = (rouge_vert << 4) | (bleu_vert)  # De nouveau, nous utilisons un bitwise OU pour collecter les bits 1.

                self.image_bytes += (octet).to_bytes(1, byteorder = "little")
                return self.image_bytes # Tout est rajouté à la bytearray().

        # ULBMP_BIG_DIFF de type R!!!!!  Nous avons trois cas où la différence est grande.
        # Dans ces cas les encodages se font sur trois bytes. Chaque cas l'organisera différement, 
        # mais l'encodage reste similaire. 
        elif rouge >= -128 and rouge <= 127:  # Le cas où le rouge qui est entre -128 et 127.
            if (vert_rouge >= -32 and vert_rouge <= 31) and (bleu_rouge >= -32 and bleu_rouge <= 31):
                
                rouge += 128 # Dans ce cas, il y a un rajout de valeurs au rouge et à la difference entre vert et rouge et bleu et rouge.
                vert_rouge += 32
                bleu_rouge += 32

                octet1 = 128  # encodage de la "tête" qui nous aidera à distinguer ces trois cas, ici c'est 1000.
                octet1 = octet | (rouge >> 4) # Nous faisons aussi un encodage pour la première moitié des rouges.
                self.image_bytes += octet1.to_bytes(1, byteorder="little")

                octet2 = rouge & 15 # pour ce cas, il faudra toujours comparer avec un 00001111
                octet2 = (octet2 << 4) | ((vert_rouge >> 2))
                self.image_bytes += octet2.to_bytes(1, byteorder="little")  # L'autre moitié est encodée ici avec 4 bits de (Dg-Dr)

                octet3 = vert_rouge >> 6
                octet3 = octet3 | bleu_rouge
                self.image_bytes += octet3.to_bytes(1, byteorder="little")  #Pour finir, le troisieme byte contiendra les deux bits restants de (Dg -Dr) ainsi que les bits de (Db - Dr)

                return self.image_bytes

        # ULBMP_BIG_DIFF de type G!!!!!  # Même encodage avec type G et B, mais pas la même organisation
        elif vert >= (-128) and vert <= 127:
            if (rouge_vert >= -32 and rouge_vert <= 31) and (bleu_vert >= -32 and bleu_vert <= 31):
                
                vert += 128  
                rouge_vert += 32
                bleu_vert += 32
                octet1 = 144  # pour identifier le bloc (10010000)
                octet1 = octet1 | (vert >> 4)  # (10010000 OU 00001111 = 1001 1111)
                self.image_bytes += octet1.to_bytes(1, byteorder="little")
                
                octet2 = vert & 15 # pour ce cas, il faudra toujours comparer avec un 00001111
                octet2 = (octet2 << 4) | ((rouge_vert >> 2))
                self.image_bytes += octet2.to_bytes(1, byteorder="little")
                
                octet3 = rouge_vert >> 6
                octet3 = octet3 | bleu_vert
                self.image_bytes += octet3.to_bytes(1, byteorder="little")
                return self.image_bytes
        
        # ULBMP_BIG_DIFF de type B!!!!!
        elif bleu >= -128 and bleu <= 127:
            if (rouge_bleu >= -32 and rouge_bleu <= 31) and (vert_bleu >= -32 and vert_bleu <= 31):
                
                bleu += 128  
                rouge_bleu += 32
                vert_bleu += 32

                octet1 = 160  # pour identifier le bloc (10010000)
                octet1 = octet1 | (bleu >> 4)  # (10010000 OU 00001111 = 1001 1111)
                self.image_bytes += octet1.to_bytes(1, byteorder="little")
                
                octet2 = bleu & 15 # pour ce cas, il faudra toujours comparer avec un 00001111
                octet2 = (octet2 << 4) | ((rouge_bleu >> 2))
                self.image_bytes += octet2.to_bytes(1, byteorder="little")
                
                octet3 = rouge_bleu >> 6
                octet3 = octet3 | vert_bleu
                self.image_bytes += octet3.to_bytes(1, byteorder="little")

                return self.image_bytes

        # ULBMP_NEW_PIXEL!!!!!  Si les couleurs sont situées loin d'elles, lencodage se fait au complet, c'est-à-dire que 
        # la 'tête' sera un byte ff, et les trois bytes restants seront les couleurs des pixels.
        if (rouge >= 128 or rouge <= -127): #or (vert >= 128 or vert <= -127) or bleu >= 128 or bleu <= -127:
            self.image_bytes += (255).to_bytes(1, byteorder = "little")
            self.image_bytes.extend([pixel2.rouge, pixel2.vert, pixel2.bleu])
        
        #if pixel2 == Pixel(128, 128, 128):
            #raise ValueError('yes', rouge)

    def save_to(self, path: str):
        """ Fonction encode l'image dans un fichier (path) en passant par une bytarray() contenant le header et les pixels. """
        
        # Pour la version trois, il y a deux types de palette, si la profondeur est 24 il faudra placer dans le header 1, sinon c'est les 3 bytes des pixels qu'il faut placer.
        
        self.header_bytearray()

        if self.version == 1: 

            for pix in self.image.pixels:  # Dans la liste de pixels, les pixels sont classés dans l'ordre de mise en place de l'image et chaqu'un est représenté par une classe Pixel.
                self.image_bytes.extend([pix.rouge, pix.vert, pix.bleu])  # Pour chaqu'un, une extraction sera faite, et les ses 3 saturations seront placées dans la bytearray().

        elif self.version == 2:  # RLE, les pixels qui se suivent et sont les mêmes sont comptés, dans la bytearray() seront placés d'abord le nombre de fois qu'un pixel est vu, ensuite le pixel.
            
            self.encodage_partiel()  # Regarde les pixels et note ceux que si répétent, puis les encode ainsi que leurs pixels.

        elif self.version == 3:  # Dans la version 3, le header change, il y a un rajout d'éléments de palette, ainsi que de rle et profondeur.
            
            self.image_bytes += self.depth.to_bytes(1, byteorder='little')  # Rajout de la profondeur et du rle.
            self.image_bytes += self.rle.to_bytes(1, byteorder='little')

            # rajout des pixels de la palette dans la bytearray()
            if self.depth != 24:
                self.palette_mapping()

            keys_pixels = []  # Liste contenant les différents keys des pixels transformés en entiers. Liste pourra être réutilisée pour depth 8 et 24.           
            octet = 0  # Variable contenant 1 octet + sa représentation.            
            liste_octets = []  # Liste de tous les octets.
            
            if self.depth < 8:  # Si la profondeur est plus petite que 24, rajout pixels un par un en suivant l'ordre de l'apparition dans la liste de pixels.  
                
                for pix in self.image.pixels:  # Pour chaque pixel de la liste de pixels, il va être comparé avec chaque valeur de la palette, jusqu'à trouver celui qui lui correspond.
                    for key, valeur in self.palette.items():
                        if Pixel.__eq__(pix, valeur) is True:  # Si ils sont égaux, la key de la valeur est enregistrée dans une liste "keys_pixels" dans l'ordre consécutif.
                            keys_pixels.append(key)  # utilisation de cette liste pour la profondeur 8
                
                compteur = 0  # Comptera les bits placées dans un byte (doivent être 8) ou si tous les pixels ont été placés.

                while len(keys_pixels) != 0:  # Avec le .pop(), chaque élément est enlevé après l'avoir 'placé' dans l'octet, jusqu'à ce que la liste est vide, pour être sur qu'elle a été parcourue à 100%.
                        
                    octet = (octet << (self.depth)) | keys_pixels.pop(0)  # octet toujours réinitialisé à 0.
                    # À l'octet est rajouté un certain nombre (self.depth) de 0 (à droite), et est enlevé un certain nombre d'éléments (self.depth) à gauche. 
                    # Ensuite avec le bitwise or, .pop(0) enlève le premier élément de la liste et compare bit par bit le résultat de la première partie.
                        
                    compteur += 1 # incrémentation par 1: montre que 1 key a été vu.
                        
                    if compteur % (8//self.depth) == 0:  # Condition compte si nous nous sommes occupés de tous les bits nécessaires pour remplir un byte. (dépend de la profondeur bpp)
                        # Si profondeur est 1 bpp: il y aura 8 pixels dans un byte, si 2 bpp: il doit y en avoir 4, ...

                        liste_octets.append(octet)  # Dans ce cas, l'octet est rajouté à la liste de octets.
                        octet = 0  # Octet et compteur sont réinitialisés à 0 pour de nouveau saisir les bits nécessaires pour créer un byte.    
                        compteur = 0

                if compteur % (8//self.depth) != 0:  # Si les pixels ne remplissent pas un byte, cela arrive quand nous nous occupons du dernier byte et qu'il n'y a plus de keys.
                        
                    octet = (octet << (8 - (compteur*self.depth))) | 0  # Le nombre de zéros qui nous manque est rajouté à droite.
                    compteur += 8 - (compteur*self.depth)  # Compteur est complet. nécessaire?
                    liste_octets.append(octet)  # Ce dernier byte est enregistré dans la liste d'octets, et chaque élément est ensuite encodé dans la bytearray().
                    
                for b in liste_octets:
                    self.image_bytes += b.to_bytes(1, byteorder='little')

            elif self.depth == 8: 
                # self.encodage_partiel()
                compteur = 1
                pixel = 0
                initial = 0
                suivant = 1
                for pix in self.image.pixels:  # Pour chaque pixel de la liste de pixels, il va être comparé avec chaque valeur de la palette, jusqu'à trouver celui qui lui correspond.
                    for key, valeur in self.palette.items():
                        if Pixel.__eq__(pix, valeur) is True:  # Si ils sont égaux, la key de la valeur est enregistrée dans une liste "keys_pixels" dans l'ordre consécutif.
                            keys_pixels.append(key)  # nous donne une liste avec les keys représentant les pixels dans l'ordre.
                while suivant < len(keys_pixels):
                    if keys_pixels[initial] == keys_pixels[suivant]: # si liste pas finie ou finie
                        if suivant != len(keys_pixels)-1:
                            compteur += 1
                            initial += 1
                            suivant += 1
                        else:
                            compteur += 1
                            while compteur > 255:
                                    self.image_bytes += (255).to_bytes(1, byteorder='little')
                                    self.image_bytes += keys_pixels[initial].to_bytes(1, byteorder='little')
                                    compteur -= 255
                            self.image_bytes += compteur.to_bytes(1, byteorder='little')
                            self.image_bytes += keys_pixels[initial].to_bytes(1, byteorder='little')
                            suivant += 1
                    else:  # Pixels ne sont pas les mêmes.
                        if suivant != len(keys_pixels)-1:  # nous ne sommes pas encore arrivés à la fin de la liste.
                            while compteur > 255:
                                    self.image_bytes += (255).to_bytes(1, byteorder='little')
                                    self.image_bytes += keys_pixels[initial].to_bytes(1, byteorder='little')
                                    compteur -= 255
                            self.image_bytes += compteur.to_bytes(1, byteorder='little')
                            self.image_bytes += keys_pixels[initial].to_bytes(1, byteorder='little')
                            compteur = 1
                            initial += 1
                            suivant += 1
                        else: # fin de liste
                            while compteur > 255:
                                    self.image_bytes += (255).to_bytes(1, byteorder='little')
                                    self.image_bytes += keys_pixels[initial].to_bytes(1, byteorder='little')
                                    compteur -= 255
                            self.image_bytes += compteur.to_bytes(1, byteorder='little')
                            self.image_bytes += keys_pixels[initial].to_bytes(1, byteorder='little')
                            compteur = 1
                            self.image_bytes += compteur.to_bytes(1, byteorder='little')
                            self.image_bytes += keys_pixels[suivant].to_bytes(1, byteorder='little')

            else:

                compteur = 1  # Initialise le compteur à 1, compte le premier pixel.
                
                for i in range(len(self.image.pixels) - 1):  # i regarde chaque pixel de la liste moins le dernier, car le 'i+1' s'occupe du dernier.
                    if Pixel.__eq__(self.image.pixels[i], self.image.pixels[i+1]):  # Si les pixel pointé par i et celui d'après sont pareils: le compteur est incrémenté.
                        compteur += 1
                    else:  # Si les 2 pixels ne sont pas égaux, il est temps d'encoder le premier type avec son compteur avant.
                        self.rajout_repetitions(i, compteur)  # ces deux informations sont envoyées.
                        compteur = 1 # compteur est réinitialisé au cas ou il y a d'autres pixels
                self.rajout_repetitions(i, compteur)  # dernier pixel.
                
        else:  # version 4

            # commencer par comparer premier pixel avec un pixel noir 
            self.premier_bloc(Pixel(0, 0, 0), self.image.pixels[0])

            for i in range(len(self.image.pixels) - 1):  # pour chaque pixel et son voisin, nous allons regarder la différence entre les pixels.
                # puis ils seront envoyés à leur fonction respective pour qu'ils puissent être encodés.
                
                self.type_bloc(self.image.pixels[i], self.image.pixels[i+1]) # retourne le type de bloc

        with open(path, 'wb') as p:
            p.write(self.image_bytes)  # La bytearray() est enregistrée dans le file.
            
class Decoder:
    """Classe pour décoder."""

    @staticmethod
    def load_from(path: str):

        """ Ouverture du fichier contenant le header et les pixels, il faut renvoyer une Image avec la width, height et liste de Pixels. """

        with open(path, 'rb') as p:  # On ouvre en 'rb' pour avoir accès au fichier en mode binaire.
            
            image_a_decoder = p.read() 

            version = int.from_bytes(image_a_decoder[5:6], byteorder = 'little')  # tester la version
            versions_possibles = [1, 2, 3, 4]

            header = int.from_bytes(image_a_decoder[6:8], byteorder = 'little')  # Valeur du header enregistrée pour trouver le début des pixels.
            
            width = int.from_bytes(image_a_decoder[8:10], byteorder = 'little')            
            height = int.from_bytes(image_a_decoder[10:12], byteorder = 'little')

            if version == 3:
                profondeur = int.from_bytes(image_a_decoder[12:13], byteorder = 'little')
                rle = int.from_bytes(image_a_decoder[13:14], byteorder = 'little')
                profondeurs_possibles = [1, 2, 4, 8, 24]
                rle_possibles =  [0, 1]

                # erreurs possibles
                if profondeur not in profondeurs_possibles: 
                    raise ValueError("La profondeur n'est pasz correcte.")
                if rle not in rle_possibles:
                    raise ValueError("La rle n'est pas correcte.")                
                if (rle == 0 and profondeur > 4) or (rle == 1 and profondeur < 8):
                    raise ValueError("La rle et la profondeur ne vont pas ensemble.") 
            
            pixels = image_a_decoder[header:]

            # Recherche d'erreurs.
            if image_a_decoder[:5] != b'ULBMP':
                raise ValueError("Le header 'ULBMP' n'est pas correctement écrit.")
            if version not in versions_possibles:
                raise ValueError("La version de l'image n'est pas juste.")

            liste_de_pixels = []

            if version == 1:
                # Dans la 1ère version, on va raise une erreur si l'aire de l'image n'est pas égale au nombre de pixels. (Puisque tous les RGB dans la liste de pixels sont séparés on doit diviser par 3.). 
                # FAIRE FONCTION CONTENANT TOUTES LES ERREURS. APPEL À CHAQUE VERSION? OU FAIRE CA A LA FIN QUAND LA LISTE SERA FINIE.
                
                if width*height != len(pixels)/3:
                    raise ValueError("Le nombre de pixels est incorrect.")
                
                # Avec une boucle while, on va rajouter dans une liste de pixels (on l'ajoutera au resultat final à la fin) les éléments Pixels (on fait appel à la première classe écrite). On incrémentera l'indice de 3 pour sauter tous les R, G, B d'un pixel et passer au suivant.
                indice = 0
                while indice < len(pixels):
                    liste_de_pixels.append(Pixel(pixels[indice],pixels[indice + 1],pixels[indice + 2]))
                    indice += 3
                
                return Image(width, height, liste_de_pixels)

            elif version == 2:
                # Dans la version 2, deux éléments sont à regarder, le nombre de répétitions qu'a un Pixel et ce Pixel.
                indice = 0
                répétitions = 0
                
                # Comme fait dans la version 1 ( METTRE DANS UNE SEULE FONCTION Au moins l'insertion. ), on regarde les quatre premiers éléments, chaqu'un a un rôle.
                while indice < len(pixels):
                    # Valeur contient le nombre de répétitions u prochain pixel.
                    nombre_de_fois = pixels[indice]
                    # Trois prochaines valeurs contiennent la saturation de chaque couleur d'un Pixel.
                    rouge, vert, bleu = pixels[indice + 1], pixels[indice + 2], pixels[indice + 3]
                    for i in range(nombre_de_fois):
                        liste_de_pixels.append(Pixel(rouge, vert, bleu))
                    indice += 4
                
                if width*height != len(liste_de_pixels):
                    raise ValueError("Le nombre de pixels est incorrect.")
                return Image(width, height, liste_de_pixels)
            
            elif version == 3:

                # Faire erreurs. => window.py
                indice = 0
                palette_mapping = {}  # Refaire un dictionnaire avec les éléments de la palette pour s'aider.
                
                profondeur = int.from_bytes(image_a_decoder[12:13], byteorder = 'little')
                profondeurs_possibles = [1, 2, 4, 8, 24]
                if profondeur not in profondeurs_possibles:
                    raise ValueError("La profondeur n'est pas bonne.")

                rle = int.from_bytes(image_a_decoder[13:14], byteorder = 'little')

                palette = image_a_decoder[14:header]

                # Pour faire error si le nombre de couleurs ≠ dans palette est supérieur.

                max_couleurs = 2**profondeur  # Taille maximale de valeurs dans la palette.

                # Transformation de palette en dictionnaire mapping pour pouvoir créer la liste de pixels plus facilement.
                compteur = 0
                # Première vue sur la palette: création d'un string qui notera l'octet complet de chaque valeur.
                octet = ''
                # On crée une liste de bytes au cas où, il y en a plus que un.
                liste_bytes = []  # Pour le décodage de la version 3, il faut regarder les profondeurs, et écrire les différents codes, sans répétitions.
                if profondeur < 8:
                    
                    for pix in pixels:  # Pour chaque byte dans la liste pixel, on va créer sa représentation binaire (celle-ci peut contenir plusieurs Pixels.
                        for bit in range(8): # Pour chaque byte, comparer bits avec 'AND'. D'un côté nous avons pix (un octet) et de l'autre nous avons 1 que l'on décale en rajoutant un certain nombre de 0 à droite. 
                            # Le AND regarde 'si la représentation binaire du 2ème nombre est dans la représentation binaire pix'. S'il y a un 'match', il y a un rajout/ concaténation dans l'octet.
                            if pix & (1 << (7 - bit)): # S'il y a un match 1 & 1 => Rajouter '1' au string.
                                octet += '1'
                            else:  # Si le match est 0 & 0 ou 1 & 0 => Rajouter '0'.
                                octet += '0'

                        liste_bytes.append(octet)
                        octet = ''
                    # Pour la suite, il est nécessaire de regarder un 'groupe' de bits dans l'octet. C'est-à-dire, si la profondeur est de 1 bit par pixel: il pourrait y avoir 8 pixel dans un octet. (taille du groupe = profondeur)
                    # Ce string crée le début de chaque pixel, s'il est nécessaire de rajouter des zéros devant pour compléter l'octet.
                    string_pixel = '0' * (8 - profondeur)
                    
                    # Contiendra les pixels, marqués comme entiers, qu'on cherchera dans la palette modifiée et nous aidera à la créer.
                    pixels_palette = []
                    
                    # p aidera à figer temporairement la boucle pour pouvoir changer ce qui se trouve dans le string en entier et le rajouter dans la liste de pixels entiers.
                    p = 0
                    
                    for oc in liste_bytes:
                        for element in range(len(oc)):
                            string_pixel += oc[element]
                            p += 1
                            
                            # Condition: p est plus petit que la profondeur, car profondeur est le nombre de bits à rajouter après les 0 dans le string créé. Il faut aussi que le nombre d'éléments dans la liste soit égal au nombre de pixels total.
                            if not p < profondeur and len(pixels_palette) < width*height  :
                                entier_pixel = int(string_pixel, 2)
                                p = 0
                                string_pixel = '0' * (8 - profondeur)
                                pixels_palette.append(entier_pixel)
                    
                    for pix in pixels_palette:
                        liste_de_pixels.append(Pixel(int.from_bytes(palette[pix*3: pix*3 + 1],byteorder = 'little'), int.from_bytes(palette[pix*3 + 1: pix*3 + 2],byteorder = 'little'), int.from_bytes(palette[pix*3 + 2: pix*3 + 3], byteorder = 'little')))
                
                elif profondeur == 8:
                    for pix in range(len(pixels)):
                        if pix % 2 == 0:
                            fois = pixels[pix]
                        else:
                            pix_nombre = pixels[pix]
                            for i in range(fois):
                                liste_de_pixels.append(Pixel(int.from_bytes(palette[pix_nombre*3: pix_nombre*3 + 1],byteorder = 'little'), int.from_bytes(palette[pix_nombre*3 + 1: pix_nombre*3 + 2],byteorder = 'little'), int.from_bytes(palette[pix_nombre*3 + 2: pix_nombre*3 + 3], byteorder = 'little')))
                    
                elif profondeur == 24:  
                    premier, deuxieme, troisieme, quatrieme = 0, 1, 2, 3  # Ces quatre valeurs regarderont des séquences de 4 bytes dans "pixels".
                    while premier < len(pixels):  # Tant que l'élément "premier" est dans "pixels".
                        repetitions = pixels[premier: deuxieme]  # répétitions sera la variable contenant la valeur représentant le nombre de fois qu'il faut lire un pixel. 
                        for i in range(int.from_bytes(repetitions, byteorder="little")):  # écrira les pixels autant de fois que les repetitions l'indiquent.
                            liste_de_pixels.append(Pixel(int.from_bytes(pixels[deuxieme:troisieme], byteorder="little"), int.from_bytes(pixels[troisieme:quatrieme], byteorder="little"), int.from_bytes(pixels[quatrieme:quatrieme+1], byteorder="little")))
                        premier += 4 
                        deuxieme += 4
                        troisieme += 4
                        quatrieme += 4
                
                return Image(width, height, liste_de_pixels)

            else: # version 4
                
                iterator = 0 # itère élément par élément
                
                while iterator < len(pixels):
                    
                    if pixels[iterator] == 255:  # ULBMP_NEW_PIXEL cas où c'est un pixel entier qui est trop différent de l'ancien pixel, si il y en a un 
                            liste_de_pixels.append(Pixel(int.from_bytes(pixels[iterator + 1], byteorder="little"), int.from_bytes(pixels[iterator + 2], byteorder="little"), int.from_bytes(pixels[iterator + 3], byteorder="little")))
                            # Nous passons au pixel suivant.
                            iterator += 4

                    else:  # bloc à identifier

                        octet = ''  # octet réunira les bits du byte en string
                        for bit in range(8):
                            if pixels[iterator] & (1 << (7 - bit)):  # avec le ET, nous comparons chaque élément du byte par un bit 1 
                                octet += '1'  # si ils ont un élément 1 au même endroit, un string 1 est ajouté à 'octet'
                            else:
                                octet += '0'  # dans le cas contraire, un 0 est rajouté 
                        iterator += 1 # on incrémente car nous avons regardé un byte.

                        if octet[0:2] == "00":  #ULBMP_SMALL_DIFF
                            rouge = 0 # initialisation de variables qui contiendront les couleurs
                            vert = 0
                            bleu = 0

                            if octet[2] == "1":  # pour chaqu'une des variables, nous ajoutons son contenu.
                                rouge += 2 ** 1
                            if octet[3] == "1":
                                rouge += 2 ** 0
                            if octet[4] == "1":
                                vert += 2 ** 1
                            if octet[5] == "1":
                                vert += 2 ** 0
                            if octet[6] == "1":
                                bleu += 2 ** 1
                            if octet[7] == "1":
                                bleu += 2 ** 0

                            if rouge - 2 > -1:  # Il faut décrémenter les variables par 2.
                                rouge -= 2
                            if vert - 2 > -1:
                                vert -= 2
                            if bleu - 2 > -1:
                                bleu -= 2
                            

                            if liste_de_pixels == []:  # Si elle est vide, il faudra regarder le pixel noirn mais celui-ci est constitué de 0s.

                                pix = Pixel(0,0,0) # comparer avec pixel noir
                                liste_de_pixels.append(Pixel(rouge + pix.rouge , vert + pix.vert, bleu + pix.bleu)) 

                            elif liste_de_pixels != []: # Sinon nous regardons le dernier pixel.
                                
                                pix = liste_de_pixels[len(liste_de_pixels)-1]
                                liste_de_pixels.append(Pixel(rouge + pix.rouge, vert + pix.vert, bleu + pix.bleu))
                            
                            octet = ''
                            
                            
                        elif octet[0:4] == "1010":  # ULBMP_BIG_DIFF_B (3 bytes)

                            octet2 = ''  # octet 2 réunira les bits du byte en string
                            octet3 = '' # octet 3 qui compose ce pixel
                            for bit in range(8):
                                if pixels[iterator] & (1 << (7 - bit)):  # avec le ET, nous comparons chaque élément du byte par un bit 1 
                                    octet2 += '1'  # si ils ont un élément 1 au même endroit, un string 1 est ajouté à 'octet'
                                else:
                                    octet2 += '0'
                                if pixels[iterator + 1] & (1 << (7 - bit)):  # avec le ET, nous comparons chaque élément du byte par un bit 1 
                                    octet3 += '1'  # si ils ont un élément 1 au même endroit, un string 1 est ajouté à 'octet'
                                else:
                                    octet3 += '0'
                            
                            iterator += 2  # Il a vu deux bytes

                            dif_bleu = octet[4:] + octet2[0:4]  # concaténation des bits pour le delta de bleu
                            bleu = 0  # variable recevra la vrai valeur
                            dif_rouge_bleu = octet2[4:] + octet3[0:2]
                            rouge_bleu = 0
                            dif_vert_bleu = octet3[2:]
                            vert_bleu = 0

                            for coul in range(len(dif_bleu)):  # Pour chaque variable contenant les différences de couleurs, nous mettons sa valeur dans une autre variable
                                if dif_bleu[coul] == '1':
                                    bleu += 2**(7-coul)
                            
                            for coul in range(len(dif_rouge_bleu)):
                                if dif_rouge_bleu[coul] == "1":
                                    rouge_bleu += 2**(5-coul)
                                
                            for coul in range(len(dif_vert_bleu)):
                                if dif_vert_bleu[coul] == "1":
                                    vert_bleu += 2**(5-coul)

                            if bleu - 128 > -1:    
                                bleu -= 128

                            rouge = rouge_bleu + bleu  # variable "rouge"

                            if rouge - 32 > -1:
                                rouge -= 32
                            
                            vert = vert_bleu + bleu

                            if vert - 32 > -1:
                                vert -=32

                            if liste_de_pixels == []:  # Si elle est vide, il faudra regarder le pixel noirn mais celui-ci est constitué de 0s.

                                pix = Pixel(0,0,0) # comparer avec pixel noir
                                liste_de_pixels.append(Pixel(rouge + pix.rouge , vert + pix.vert, bleu + pix.bleu)) 

                            if liste_de_pixels != []: # Sinon nous regardons le dernier pixel.
                                
                                pix = liste_de_pixels[len(liste_de_pixels)-1]
                                liste_de_pixels.append(Pixel(rouge + pix.rouge, vert + pix.vert, bleu + pix.bleu))
                            

                            octet = ''
                            octet2 = ''
                            octet3 = ''

                        elif octet[0:4] == "1000":  # ULBMP_BIG_DIFF_R (3 bytes)

                            octet2 = ''  # octet 2 réunira les bits du byte en string
                            octet3 = '' # octet 3 qui compose ce pixel
                            for bit in range(8):
                                if pixels[iterator] & (1 << (7 - bit)):  # avec le ET, nous comparons chaque élément du byte par un bit 1 
                                    octet2 += '1'  # si ils ont un élément 1 au même endroit, un string 1 est ajouté à 'octet'
                                else:
                                    octet2 += '0'
                                if pixels[iterator + 1] & (1 << (7 - bit)):  # avec le ET, nous comparons chaque élément du byte par un bit 1 
                                    octet3 += '1'  # si ils ont un élément 1 au même endroit, un string 1 est ajouté à 'octet'
                                else:
                                    octet3 += '0'
                            
                            iterator += 2  # Il a vu deux bytes

                            dif_rouge = octet[4:] + octet2[0:4]  # concaténation des bits pour le delta de bleu
                            rouge = 0  # variable recevra la vrai valeur
                            dif_vert_rouge = octet2[4:] + octet3[0:2]
                            vert_rouge = 0
                            dif_bleu_rouge = octet3[2:]
                            bleu_rouge = 0

                            for coul in range(len(dif_rouge)):  # Pour chaque variable contenant les différences de couleurs, nous mettons sa valeur dans une autre variable
                                if dif_rouge[coul] == '1':
                                    rouge += 2**(7-coul)
                            
                            for coul in range(len(dif_vert_rouge)):
                                if dif_vert_rouge[coul] == "1":
                                    vert_rouge += 2**(5-coul)
                                
                            for coul in range(len(dif_bleu_rouge)):
                                if dif_bleu_rouge[coul] == "1":
                                    bleu_rouge += 2**(5-coul)

                            if rouge - 128 > -1:    
                                rouge -= 128

                            vert = vert_rouge + rouge  # variable "vert"

                            if vert - 32 > -1:
                                vert -= 32
                            
                            bleu = bleu_rouge + rouge

                            if bleu - 32 > -1:
                                bleu -=32

                            if liste_de_pixels == []:  # Si elle est vide, il faudra regarder le pixel noirn mais celui-ci est constitué de 0s.

                                pix = Pixel(0,0,0) # comparer avec pixel noir
                                liste_de_pixels.append(Pixel(rouge + pix.rouge , vert + pix.vert, bleu + pix.bleu)) 

                            if liste_de_pixels != []: # Sinon nous regardons le dernier pixel.
                                
                                pix = liste_de_pixels[len(liste_de_pixels)-1]
                                liste_de_pixels.append(Pixel(rouge + pix.rouge, vert + pix.vert, bleu + pix.bleu))
                            

                            octet = ''
                            octet2 = ''
                            octet3 = ''
                        
                        elif octet[0:4] == "1001":  # ULBMP_BIG_DIFF_G (3 bytes)

                            octet2 = ''  # octet 2 réunira les bits du byte en string
                            octet3 = '' # octet 3 qui compose ce pixel
                            for bit in range(8):
                                if pixels[iterator] & (1 << (7 - bit)):  # avec le ET, nous comparons chaque élément du byte par un bit 1 
                                    octet2 += '1'  # si ils ont un élément 1 au même endroit, un string 1 est ajouté à 'octet'
                                else:
                                    octet2 += '0'
                                if pixels[iterator + 1] & (1 << (7 - bit)):  # avec le ET, nous comparons chaque élément du byte par un bit 1 
                                    octet3 += '1'  # si ils ont un élément 1 au même endroit, un string 1 est ajouté à 'octet'
                                else:
                                    octet3 += '0'
                            
                            iterator += 2  # Il a vu deux bytes

                            dif_vert = octet[4:] + octet2[0:4]  # concaténation des bits pour le delta de bleu
                            vert = 0  # variable recevra la vrai valeur
                            dif_rouge_vert = octet2[4:] + octet3[0:2]
                            rouge_vert = 0
                            dif_bleu_vert = octet3[2:]
                            bleu_vert = 0

                            for coul in range(len(dif_vert)):  # Pour chaque variable contenant les différences de couleurs, nous mettons sa valeur dans une autre variable
                                if dif_vert[coul] == '1':
                                    vert += 2**(7-coul)
                            
                            for coul in range(len(dif_rouge_vert)):
                                if dif_rouge_vert[coul] == "1":
                                    rouge_vert += 2**(5-coul)
                                
                            for coul in range(len(dif_bleu_vert)):
                                if dif_bleu_vert[coul] == "1":
                                    bleu_vert += 2**(5-coul)

                            if vert - 128 > -1:    
                                vert -= 128

                            bleu = bleu_vert + vert  # variable "vert"

                            if bleu - 32 > -1:
                                bleu -= 32
                            
                            rouge = rouge_vert + vert

                            if rouge - 32 > -1:
                                rouge -=32

                            if liste_de_pixels == []:  # Si elle est vide, il faudra regarder le pixel noirn mais celui-ci est constitué de 0s.

                                pix = Pixel(0,0,0) # comparer avec pixel noir
                                liste_de_pixels.append(Pixel(rouge + pix.rouge , vert + pix.vert, bleu + pix.bleu)) 

                            if liste_de_pixels != []: # Sinon nous regardons le dernier pixel.
                                
                                pix = liste_de_pixels[len(liste_de_pixels)-1]
                                liste_de_pixels.append(Pixel(rouge + pix.rouge, vert + pix.vert, bleu + pix.bleu))
                            

                            octet = ''
                            octet2 = ''
                            octet3 = ''

                        elif octet[0:2] == "01": # cas de ULBMP INTERMEDIATE DIFF (2 bytes à regarder)
                            
                            octet2 = ''
                            for bit in range(8):
                                if pixels[iterator] & (1 << (7 - bit)):  # avec le ET, nous comparons chaque élément du byte par un bit 1 
                                    octet2 += '1'  # si ils ont un élément 1 au même endroit, un string 1 est ajouté à 'octet'
                                else:
                                    octet2 += '0'
                            iterator += 1
                            
                            dif_vert = octet[2:]
                            vert = 0
                            dif_rouge_vert = octet2[:4]
                            rouge_vert = 0
                            dif_bleu_vert = octet2[4:]
                            bleu_vert = 0

                            for coul in range(len(dif_vert)):
                                if dif_vert[coul] == "1":
                                    vert += 2**(5 - coul)
                            
                            for coul in range(len(dif_rouge_vert)):
                                if dif_rouge_vert[coul] == "1":
                                    rouge_vert += 2**(3 - coul)

                            for coul in range(len(dif_bleu_vert)):
                                if dif_bleu_vert[coul] == "1":
                                    bleu_vert += 2**(3 - coul)


                            vert -= 32
                            
                            rouge_vert -= 8

                            rouge = rouge_vert + vert

                            if bleu_vert - 8 > -1:
                                bleu_vert -= 8

                            bleu = bleu_vert + vert

                            if liste_de_pixels == []:  # Si elle est vide, il faudra regarder le pixel noirn mais celui-ci est constitué de 0s.

                                pix = Pixel(0,0,0) # comparer avec pixel noir
                                liste_de_pixels.append(Pixel(rouge + pix.rouge , vert + pix.vert, bleu + pix.bleu)) 

                            if liste_de_pixels != []: # Sinon nous regardons le dernier pixel.
                                
                                pix = liste_de_pixels[len(liste_de_pixels)-1]
                                liste_de_pixels.append(Pixel(rouge + pix.rouge, vert + pix.vert, bleu + pix.bleu))
                            

                            octet =""
                            octet2 = ""
                            
                                
                    
            return Image(width, height, liste_de_pixels)
