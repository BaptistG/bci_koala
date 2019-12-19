import numpy as np

def b0(delta_f, fc, fe, G):
    return 2*np.pi * G *delta_f *np.sin(2*np.pi*fc/fe)/fe

def a1(delta_f, fc, fe, G):
    return -2 * ((1-2*np.pi * G *delta_f/fe)**0.5) * np.cos(2*np.pi*fc/fe)

def a2(delta_f, fe, G):
    return 1 - (2*np.pi * G *delta_f/fe)

def get_filter_coefs(freqs, G=0.6, fe = 256, delta_f=1):
    coefs = {}
    for freq in freqs:
        coefs[freq] = {
            'b0': b0(delta_f, freq, fe, G),
            'a1': a1(delta_f, freq, fe, G),
            'a2': a2(delta_f, fe, G)
        }
    return coefs


def apply_filter(x_n, y_n_1, y_n_2, fc, coefs):
    coef = coefs[fc]
    return coef['b0'] * x_n - coef['a1'] * y_n_1 - coef['a2'] * y_n_2

def puissance(y_n, z_n_1, alpha=0.96):
    z_n = ((1 - alpha)*(y_n**2) + alpha*(z_n_1**2))**0.5
    return z_n


def votes(puissances):
    gauche = puissances[7.5]
    avance = puissances[11]
    droite = puissances[13.5]

    v_gauche = 0
    v_avance = 0
    v_droite = 0
    v_none = 0

    N = len(gauche)
    for i in range(N):
        if max(gauche[i], avance[i], droite[i]) < 0.0025:
                v_none += 1
        elif gauche[i] > avance[i] and gauche[i] > droite[i]:
            v_gauche += 1
        elif avance[i] > gauche[i] and avance[i] > droite[i]:
            v_avance += 1
        elif droite[i] > gauche[i] and droite[i] > avance[i]:
            v_droite += 1



    m = max(v_gauche, v_droite, v_avance, v_none)


    if m == v_gauche:
        vote = 'TurnLeft'
    elif m == v_droite:
        vote = 'TurnRight'
    elif m == v_avance:
        vote = 'Forward'
    else:
        vote = 'None'

    return vote
