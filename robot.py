import os

try:
    from pidog import Pidog
    from time import sleep
    PIDOG_AVAILABLE = True
except ImportError:
    PIDOG_AVAILABLE = False
    print("[⚠️] Bibliothèque 'pidog' indisponible. Les fonctions robotiques sont désactivées.")

# Initialiser le robot uniquement si la bibliothèque est dispo
my_dog = Pidog(head_init_angles=[0, 0, -30]) if PIDOG_AVAILABLE else None

def awake_dog():
    """
    Réveille le robot : il se lève et se met en position debout.
    """
    if not PIDOG_AVAILABLE:
        print("[AWAKE] Fonction désactivée (pidog non disponible).")
        return

    my_dog.do_action('stand', speed=50)
    my_dog.wait_all_done()
    print("[AWAKE] Le chien est debout et actif.")

def sleep_dog():
    """
    Endort le robot : il s'assoit et s'éteint.
    """
    if not PIDOG_AVAILABLE:
        print("[SLEEP] Fonction désactivée (pidog non disponible).")
        return

    my_dog.do_action('sit', speed=40)
    my_dog.wait_all_done()
    my_dog.close()
    print("[SLEEP] Le chien est assis et éteint.")

def start_patrol():
    if not PIDOG_AVAILABLE:
        print("[PATROL] (mock) Début de patrouille.")
        return
    my_dog.do_action('forward', speed=35)
    for angle in range(-30, 31, 10):
        my_dog.head_move([[0, angle, -30]], immediately=True, speed=40)
        sleep(0.3)
    for angle in range(30, -31, -10):
        my_dog.head_move([[0, angle, -30]], immediately=True, speed=40)
        sleep(0.3)
    print("[PATROL] Le chien patrouille en ligne droite.")

def stop_patrol():
    if not PIDOG_AVAILABLE:
        print("[STOP] (mock) Arrêt de la patrouille.")
        return
    my_dog.do_action('stop', speed=20)
    my_dog.head_move([[0, 0, -30]], immediately=True, speed=60)
    print("[STOP] Le chien s'arrête et regarde devant lui.")


def close_dog():
    if not PIDOG_AVAILABLE:
        print("[CLOSING] Fonction désactivée (pidog non disponible).")
        return
    my_dog.close()
    
