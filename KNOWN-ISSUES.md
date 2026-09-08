# Known Issues

- The `pool` category carries no `.localized.json`, but `build_registry.py` still emits its Lists into
  each language's `lists.json`. The site is expected to skip a category it has no display name
  for; if it does not, the registry build needs an explicit skip rule.
- `.community/featured.json` no longer features a List: the featured entry pointed at
  `awards/cannes/cannes-2026`, which the pool merge removed. Pick a new featured List once the
  pool's visibility is settled.
- Ceremony source data drifts between the per-prize and per-year Lists (translated titles, winner
  transliteration and punctuation). The merge folded those pairs with fuzzy matching; every
  original List still reproduces exactly from the pool, but new contributions should keep one
  spelling per record.
