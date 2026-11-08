#!/usr/bin/env python3
"""RLL: event-jump zero-phase graph / prime-exponent factor lattice.
Classical exact arithmetic, not novel cosmology or new physical law.
"""
from array import array
from math import gcd, isqrt


def _values(values):
    seq = tuple(values)
    if not seq:
        raise ValueError("MMC requires at least one integer")
    if any(type(n) is not int for n in seq):
        raise TypeError("exact integers only (no float, bool or str)")
    return tuple(abs(n) for n in seq)


def jump_graph(values, *, trace=False, gcd_fn=gcd):
    """At period M, next n-alignment occurs at M*(n/gcd(M,n)).
    The GCD is Euclid underneath. This is NOT a novel independent algorithm.
    """
    seq = _values(values)
    if 0 in seq:
        return (0, []) if trace else 0
    period = 1
    edges = []
    for n in seq:
        g = gcd_fn(period, n)
        multiplier = n // g
        next_period = period * multiplier
        if trace:
            edges.append([period, n, g, multiplier, next_period])
        period = next_period
    return (period, edges) if trace else period


def prime_trial_factors(n):
    """Trial division exact, potentially slow for large prime inputs."""
    if n < 1:
        raise ValueError("factor domain n>=1")
    out = {}
    exp = 0
    while n % 2 == 0:
        exp += 1
        n //= 2
    if exp:
        out[2] = exp
    d = 3
    while d <= isqrt(n):
        exp = 0
        while n % d == 0:
            exp += 1
            n //= d
        if exp:
            out[d] = exp
        d += 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def _join_factors(vals, factorizer):
    if 0 in vals:
        return 0
    maximum = {}
    for n in vals:
        for p, e in factorizer(n).items():
            if e > maximum.get(p, 0):
                maximum[p] = e
    product = 1
    for p, e in maximum.items():
        product *= p ** e
    return product


def prime_lattice_trial(values):
    """Join prime valuation lattice: v_p(LCM) = max_i v_p(n_i)."""
    return _join_factors(_values(values), prime_trial_factors)


class SmallestPrimeFactorGraph:
    """Reusable uint32 SPF sieve, explicit 4*(limit+1) payload memory.
    Zero in table denotes prime for n>=2; 0/1 are special, not missing.
    """
    def __init__(self, limit):
        if type(limit) is not int or not 2 <= limit <= (2**32 - 1):
            raise ValueError("SPF limit must be integer 2..2^32-1")
        self.limit = limit
        self.spf = array("I", [0]) * (limit + 1)
        for p in range(2, isqrt(limit) + 1):
            if self.spf[p] == 0:
                for m in range(p*p, limit+1, p):
                    if self.spf[m] == 0:
                        self.spf[m] = p

    @property
    def payload_bytes(self):
        return self.spf.itemsize * len(self.spf)

    def factors(self, n):
        if not 1 <= n <= self.limit:
            raise ValueError("SPF domain exceeded: no silent fallback")
        out = {}
        while n > 1:
            p = self.spf[n] or n
            out[p] = out.get(p, 0) + 1
            n //= p
        return out

    def lcm(self, values):
        seq = _values(values)
        if any(n > self.limit for n in seq if n):
            raise ValueError("SPF input exceeds precomputed limit")
        return _join_factors(seq, self.factors)
