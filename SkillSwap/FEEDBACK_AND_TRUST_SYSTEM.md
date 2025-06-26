# Feedback & Trust System

## Rated Metrics
- Skill quality (1–5)
- Reliability (1–5)
- Communication (1–5)

## Written Reviews
- Optional text field (max 500 chars)
- Displayed on user profile with date stamp.

## Trust Score Calculation
```
trust_score = (avg_skill + avg_reliability + avg_comm) / 3
```
- Decay factor: older reviews weight ↓10%/month.

## Moderation Flags
- >3 consecutive 1-star reviews → auto-flag.
- Admin approval required before profile removal.
