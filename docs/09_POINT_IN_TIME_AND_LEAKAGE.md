# Point-in-Time Correctness and Leakage Prevention

## 1. Core rule

For analysis cutoff T, features may only contain information available at or before T according to the defined information timestamp.

## 2. Timestamps

Store:
- `event_time`;
- `published_at` for news;
- `retrieved_at`;
- `as_of`;
- `available_at`.

When provider availability is ambiguous, use the more conservative `available_at` semantics.

## 3. News cutoff

```text
include article iff available_at <= T
```

Later revisions require a recorded revision/availability time.

## 4. Market cutoff

Only completed bars available by T may be used. An intraday bar still forming at T is not treated as complete.

## 5. Indicator cutoff

Indicators must be calculated over a series clipped at T.

## 6. Training leakage

For prediction at t of t+h:
- features at t use information <= t;
- labels may reference future outcomes;
- future outcomes are never part of model inputs.

## 7. Survivorship bias

Full-universe historical claims are out of scope for v1. If added later, preserve historical universe membership.

## 8. Corporate actions

Record whether price series are raw or adjusted and preserve provider adjustment semantics.

## 9. News duplication

Do not count syndicated copies as independent information. Use duplicate groups and canonical article records.

## 10. Mandatory look-ahead unit test

Create two fixture sets identical through T but differing only after T. Features and signal at T must remain identical. Any difference is a blocking defect.
