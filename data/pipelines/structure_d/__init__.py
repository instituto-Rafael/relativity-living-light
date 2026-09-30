"""Structure-D package surface.

The package initializer is intentionally dependency-light. Legacy numerical
symbols are loaded lazily from .likelihood only when explicitly requested.
This lets zero-dependency successors live in the same namespace without
implicitly importing NumPy/SciPy.
"""

__all__ = [
    "aic",
    "bic",
    "chi2",
    "chi2_with_covariance",
    "evaluate_model",
    "evaluate_posterior",
    "is_physically_stable",
    "load_csv",
    "log_likelihood",
    "log_prior",
]


def __getattr__(name):
    if name in __all__:
        from . import likelihood
        return getattr(likelihood, name)
    raise AttributeError(name)
