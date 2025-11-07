

## Redundancy / Abstraction Cleanup Targets

1. ~~**Dead `refresh` export in `usePaperFeed`**~~ ✅ Removed; hook now only returns the fields that callers actually use.
2. ~~**Unnecessary year normalization**~~ ✅ `pickYear` trusts the validated config and no longer recalculates min/max on every call.
3. ~~**Duplicate `pickTarget` invocations in `loadBatch`**~~ ✅ Loop now honors the `canRetry` flag returned from `samplePaper` instead of re-invoking `pickTarget`.
