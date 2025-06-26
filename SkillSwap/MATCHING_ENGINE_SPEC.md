# Matching Engine Spec

## Matching Pairs & Chains
- **Pair**: Match A\u21C4B if skills intersect and availability overlaps.
- **Chain**: A\u2192B\u2192C\u2192A for triangular swaps when direct match absent.

## Constraints
- **Time window**: \u00b130 min tolerance.
- **Location**: radius filter or virtual flag.

## Barter Logic
- **1hr:1hr** by default.
- **Point system**: 1 credit = 1 min; supports fractional trades.
- **Fairness check**: total credits on both sides \u22645% variance.

### Pseudocode
```python
def find_matches(user):
    candidates = query_users(skill=user.desired, avail=user.avail)
    for c in candidates:
        if hours_match(user, c):
            yield Pair(user, c)
    if no_pair:
        yield from find_chains(user)
```
