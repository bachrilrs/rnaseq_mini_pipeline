import numpy as np

def normalize(Xc):
    # normalize

    std = Xc.std(axis=0 , ddof=0)
    std[std == 0] = 1.0
    return Xc/std , std

def center(X):
    # center
    mean = X.mean(axis=0)
    return X - X.mean(axis=0) , mean 

def covariance(X):
    # covariance matrix
    return np.cov(X,rowvar=False)

def vals_vecs(mcov):
    e_vals , e_vecs = np.linalg.eig(mcov)
    return [e_vals , e_vecs]

def var_explain(e_vals):
    # explained variance
    var_exp = e_vals / e_vals.sum()
    return var_exp

def scores_f(X,e_vecs):
    return X @ e_vecs

def acp(x, normalised=False):
    # centrer
    Xc , mean= center(x)

    # Normaliser
    if normalised:
        Xn ,std = normalize(Xc)
    else:
        Xn=Xc
        std = np.ones(x.shape[1])
    
    # Mcov
    mcov = np.cov(Xn,rowvar=False)
    # valeurs propres vecteurs propres
    e_vals , e_vecs = np.linalg.eig(mcov)

    # 5) Tri décroissant des valeurs propres
    idx = np.argsort(e_vals)[::-1]
    e_vals = e_vals[idx]
    e_vecs = e_vecs[:, idx] 

    # Proportion de variance expliqué
    var_exp = var_explain(e_vals)

    # Scores Projection d'individus
    scores = scores_f(Xn, e_vecs)


    return {
        'eigvals' : e_vals,
        'Variance_expliquee' : var_exp,
        'Scores' : scores,
        'Vecteurs_propres' : e_vecs,
        'Matrice_covariance' : mcov,
        'center' : mean,
        'scale'  : std,
        'normalised' : normalised,
    }
