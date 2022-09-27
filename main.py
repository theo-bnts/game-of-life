import sys
import os
import random
import screeninfo
import tkinter

# constantes globales
probabilite_cellule_vivante = 20

# variables globales
nombre_voisins_naissance, nombre_voisins_survie = None, None
nombre_lignes, nombre_colonnes = None, None
taille_cellule = None
nombre_generations, maximum_generations = None, None
frequence_en_secondes = None
grille_affichee, grille_suivante = None, None
fenetre, canvas = None, None

def main():
    """
    Fonction principale du programme.
    """

    global frequence_en_secondes, fenetre

    try:
        initialisation()
        vie()
    except KeyboardInterrupt:
        effacer_console()
        exit('Programme interrompu par l\'utilisateur.')
    except Exception:
        effacer_console()
        exit('Une erreur inconnue est survenue.')

##########################################################################
#                                Niveau 0                                #
##########################################################################

def initialisation():
    """
    Initialise les paramètres du jeu et la première grille.
    """

    global frequence_en_secondes

    frequence_en_secondes = 2

    choisir_parametres()
    creer_grille_initiale()
    creer_fenetre()
    afficher_grille()

def vie():
    """
    Boucle principale du programme.
    """

    global fenetre

    algorithmie()
    afficher_grille()
    
    fenetre.after(frequence_en_secondes * 1000, vie)
    fenetre.mainloop()

##########################################################################
#                                Niveau 1                                #
##########################################################################

def choisir_parametres():
    """
    Demande à l'utilisateur de choisir les paramtètres initiaux du jeu.
    """

    choisir_mode_de_jeu()
    choisir_taille_grille()
    choisir_nombre_generations()

def creer_grille_initiale():
    """
    Crée une liste de listes (la grille) qui contient aléatoirement des 0 et des 1 pour représenter les cellules.
    """

    global nombre_lignes, nombre_colonnes, grille_affichee, grille_suivante

    grille_suivante = []

    for ligne in range(nombre_lignes):
        grille_ligne = []

        for colonne in range(nombre_colonnes):
            if random.randint(0, 100) <= probabilite_cellule_vivante:
                grille_ligne += [1]
            else:
                grille_ligne += [0]

        grille_suivante += [grille_ligne]

def creer_fenetre():
    """
    Initialise la fenêtre de jeu.
    """

    global nombre_lignes, nombre_colonnes, taille_cellule, canvas, fenetre

    fenetre = tkinter.Tk()
    fenetre.title('Jeu de la vie & Day and night')
    fenetre.resizable(False, False)
    fenetre.protocol('WM_DELETE_WINDOW', fermer_fenetre)

    canvas = tkinter.Canvas(fenetre, width = taille_cellule * nombre_colonnes, height = taille_cellule * nombre_lignes, bg = 'white')
    canvas.bind('<Button-1>', canvas_clique)
    canvas.pack()

    slider = tkinter.Scale(fenetre, from_=1, to=10, orient=tkinter.HORIZONTAL, label='Fréquence (secs)', command=slider_deplace)
    slider.set(frequence_en_secondes)
    slider.pack()

def afficher_grille():
    """
    Affiche la grille dans la fenêtre.
    """

    global nombre_lignes, nombre_colonnes, grille_affichee, grille_suivante

    for ligne in range(nombre_lignes):
        for colonne in range(nombre_colonnes):
            if grille_suivante[ligne][colonne] == 0:
                if (grille_affichee == None or grille_affichee[ligne][colonne] == 1):
                    afficher_cellule(ligne, colonne, 'white')
            else:
                if (grille_affichee == None or grille_affichee[ligne][colonne] == 0):
                    afficher_cellule(ligne, colonne, 'black')

    #copie sans référence
    grille_affichee = [row[:] for row in grille_suivante]

def algorithmie():
    """
    Regroupe les fonctions qui traitent les étapes du jeu.
    """

    global nombre_generations

    creer_grille_suivante()

    if not (grilles_differentes()):
        effacer_console()
        exit('Fin du programme. La grille ne change plus.')

    if (nombre_generations == maximum_generations):
        effacer_console()
        exit('Fin du programme. Nombre de générations maximum atteint.')
    
    nombre_generations += 1

##########################################################################
#                                Niveau 2                                #
##########################################################################

def choisir_mode_de_jeu():
    """
    Demande à l'utilisateur de choisir un mode de jeu.
    """

    global nombre_voisins_naissance, nombre_voisins_survie

    effacer_console()
    print('\t1 - Jeu de la vie')
    print('\t2 - Day & Night')

    mode_de_jeu = demander_nombre('Entrez le numéro du mode de jeu : ', 1, 2)

    if mode_de_jeu == 1:
        nombre_voisins_naissance = [3]
        nombre_voisins_survie = [2, 3]
    else:
        nombre_voisins_naissance = [3, 6, 7, 8]
        nombre_voisins_survie = [3, 4, 6, 7, 8]

def choisir_nombre_generations():
    """
    Demande à l'utilisateur de choisir le nombre de générations.
    """

    global nombre_generations, maximum_generations

    effacer_console()
    maximum_generations = demander_nombre('Entrez le nombre de générations (1-1000) : ', 1, 1000)

    nombre_generations = 0

def choisir_taille_grille():
    """
    Demande à l'utilisateur de choisir la taille de la grille.
    """

    global nombre_lignes, nombre_colonnes, taille_cellule

    effacer_console()

    nombre_lignes = demander_nombre('Entrez le nombre de lignes (10-100) : ', 10, 100)
    nombre_colonnes = demander_nombre('Entrez le nombre de colonnes (10-100) : ', 10, 100)

    monitors = screeninfo.get_monitors()

    min_viewport_width = min([monitor.width for monitor in monitors])
    min_viewport_height = min([monitor.height for monitor in monitors]) - 300

    taille_cellule = min(min_viewport_width // nombre_colonnes, min_viewport_height // nombre_lignes)

def creer_grille_suivante():
    """
    Analyse la grille actuelle et détermine quelles cellules vivent et meurent dans la grille suivante.
    """

    global nombre_lignes, nombre_colonnes, nombre_voisins_naissance, nombre_voisins_survie, grille_affichee, grille_suivante

    for ligne in range(nombre_lignes):
        for colonne in range(nombre_colonnes):
            voisins_en_vie = obtenir_nombre_voisins_vivants(ligne, colonne)

            if grille_affichee[ligne][colonne] == 0 and (voisins_en_vie in nombre_voisins_naissance):
                grille_suivante[ligne][colonne] = 1
            elif not (grille_affichee[ligne][colonne] == 1 and (voisins_en_vie in nombre_voisins_survie)):
                grille_suivante[ligne][colonne] = 0
            else:
                grille_suivante[ligne][colonne] = grille_affichee[ligne][colonne]

def grilles_differentes():
    """
    Vérifie si la grille actuelle est la même que la grille suivante.

    :return : Boolean - Indique si la grille de la génération actuelle est la même que celle de la génération suivante.
    """

    global nombre_lignes, nombre_colonnes, grille_affichee, grille_suivante

    for ligne in range(nombre_lignes):
        for colonne in range(nombre_colonnes):
            if not grille_affichee[ligne][colonne] == grille_suivante[ligne][colonne]:
                return True

    return False

def afficher_cellule(ligne, colonne, couleur):
    """
    Affiche une cellule de la grille dans le canvas.
    """

    global nombre_colonnes, nombre_lignes, taille_cellule, canvas

    canvas.create_rectangle(
        (nombre_colonnes - colonne) * taille_cellule,
        (nombre_lignes - ligne) * taille_cellule,
        (nombre_colonnes - colonne - 1) * taille_cellule,
        (nombre_lignes - ligne - 1) * taille_cellule,
        fill=couleur,
        outline='black'
    )

##########################################################################
#                                Niveau 3                                #
##########################################################################

def obtenir_nombre_voisins_vivants(ligne, colonne):
    """
    Compte le nombre de cellules vivantes entourant une cellule.

    :param ligne : Int - Rangée de la cellule.
    :param colonne : Int - Colonne de la cellule.

    :return : Int - Nombre de cellules vivantes entourant la cellule.
    """

    global nombre_lignes, nombre_colonnes, grille_affichee

    nombre_voisins_vivants = 0

    #range n'inclue pas le nombre passé en second paramètre
    for i in range(-1, 1 + 1):
        for j in range(-1, 1 + 1):
            if not (i == 0 and j == 0):
                # on sélectionne toutes les cellules voisines
                # le modulo permet de faire en sorte que les cellules sur les bords de la grille soient considérées comme voisines des cellules sur l'autre bord de la grille
                nombre_voisins_vivants += grille_affichee[(ligne + i) % nombre_lignes][(colonne + j) % nombre_colonnes]

    return nombre_voisins_vivants

def canvas_clique(event):
    """
    Détermine la cellule cliquée et la fait vivre ou mourir.

    :param event : Event - Événement de la souris.
    """

    global nombre_lignes, nombre_colonnes, taille_cellule, grille_affichee, grille_suivante

    ligne = nombre_lignes - 1 - event.y // taille_cellule
    colonne = nombre_colonnes - 1 - event.x // taille_cellule

    grille_affichee[ligne][colonne] = 1 - grille_affichee[ligne][colonne]

    if grille_affichee[ligne][colonne] == 0:
        couleur_cellule = 'white'
    else:
        couleur_cellule = 'black'

    afficher_cellule(ligne, colonne, couleur_cellule)

def slider_deplace(value):
    """
    Modifie la vitesse de rafraîchissement du jeu.

    :param value : Int - Valeur du slider.
    """

    global frequence_en_secondes

    frequence_en_secondes = int(value)

def fermer_fenetre():
    """
    Ferme la fenêtre.
    """

    global fenetre

    effacer_console()
    print('Fin du programme. Fenêtre fermée.')

    fenetre.destroy()

##########################################################################
#                                 Outils                                 #
##########################################################################

def effacer_console():
    """
    Efface la console en utilisant une commande système basée sur le système d'exploitation de l'utilisateur.
    """

    if sys.platform.startswith('win'):
        os.system('cls')

    elif sys.platform.startswith('linux'):
        os.system('clear')

    else:
        print('Impossible d\'effacer la console. Votre OS n\'est pas supporté.')

def demander_nombre(message, minimum, maximum):
    """
    Demande à l'utilisateur d'entrer un nombre entier entre des limites données (minimum et maximum).

    :param message : String - Chaîne de caractères à utiliser pour demander à l'utilisateur d'entrer des données.
    :param minimum : Int - Limite inférieure.
    :param maximum : Int - Limite supérieure.
    
    :return : La valeur d'entrée valide que l'utilisateur a saisie.
    """

    while True:
        try:
            value = int(input(message))
        except ValueError:
            print('La saisie n\'est pas un nombre entier.')
            continue

        if value < minimum or value > maximum:
            print('La valeur doit être comprise entre {0} et {1}.'.format(minimum, maximum))
        else:
            break

    return value

main()