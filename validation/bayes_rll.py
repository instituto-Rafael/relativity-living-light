import numpy as np
import emcee
from validation.load_data_numpy_legacy import load_real_data

z, y, yerr = load_real_data()

H0 = 70.0

# ------------------------
# MODELO PARAMÉTRICO RLL
# ε = parâmetro livre
# ------------------------
def model(z, eps):
    return H0 * np.sqrt(0.3*(1+z)**3 + 0.7) + eps*np.log(1+z)

def log_likelihood(theta):
    eps = theta[0]
    pred = model(z, eps)
    sigma2 = yerr**2
    return -0.5 * np.sum((y - pred)**2 / sigma2)

def log_prior(theta):
    eps = theta[0]
    if -5 < eps < 5:
        return 0.0
    return -np.inf

def log_probability(theta):
    lp = log_prior(theta)
    if not np.isfinite(lp):
        return -np.inf
    return lp + log_likelihood(theta)

# ================================
# MCMC
# ================================
ndim = 1
nwalkers = 20

pos = 0.1 * np.random.randn(nwalkers, ndim)

sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability)
sampler.run_mcmc(pos, 500, progress=False)

samples = sampler.get_chain(discard=100, flat=True)

best_eps = float(np.median(samples[:,0]))

result = {
    "best_eps": best_eps,
    "eps_std": float(np.std(samples[:,0]))
}

print("BAYES RESULT:", result)
