# RAFAELIA Vertical Slice V1 — RLL falsification adapter

**Canonical operational authority:** `rafaelmeloreisnovo/Mapa` draft PR #95.  
**RLL role:** scientific falsification domain.  
**Policy:** `claim_allowed=false` until the full scientific contract is satisfied and independently reviewed.

A scientific claim advances only when all factors exist:

```text
C = D × B × M × F × R
```

- `D`: versioned data;
- `B`: explicit baseline;
- `M`: declared metric;
- `F`: executable falsifier;
- `R`: reproducible receipt.

The current vertical slice verifies only file/container structure for an APK, a chat-export ZIP and seven PNG files. It produces no cosmological result and must not modify canonical RLL scientific outputs.

RLL integration requirements:

1. map each scientific claim to exact source/dataset IDs;
2. declare baseline and metric before execution;
3. use multiple fixed seeds when stochastic behavior exists;
4. preserve favorable and unfavorable results;
5. emit receipts bound to the exact commit and environment;
6. send decisions, contradictions and gaps back to Mapa;
7. leave any absent factor as `TOKEN_VAZIO`.

Syntax-valid YAML, green CI or repeated numerical output cannot substitute for scientific evidence.
