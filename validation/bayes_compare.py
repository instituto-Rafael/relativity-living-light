import json
import numpy as np
from validation.load_data_numpy_legacy import load_real_data
from validation.bayes_rll import model, best_eps

z, y, yerr = load_real_data()

lcdm = 70*np.sqrt(0.3*(1+z)**3 + 0.7)
rll = model(z, best_eps)

chi_lcdm = np.sum((y - lcdm)**2 / yerr**2)
chi_rll  = np.sum((y - rll)**2 / yerr**2)

result = {
    "chi2_lcdm": float(chi_lcdm),
    "chi2_rll": float(chi_rll),
    "best_eps": float(best_eps),
    "winner": "RLL" if chi_rll < chi_lcdm else "LCDM"
}

with open("validation_outputs/bayes_result.json", "w") as f:
    json.dump(result, f)

print("FINAL BAYES:", result)
