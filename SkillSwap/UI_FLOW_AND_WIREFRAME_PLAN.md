# UI Flow & Wireframe Plan

## 1. Onboarding Screen
- **Goal**: Collect bio, skills, availability.
- **Wireframe**: Multi-step form with progress bar.
- **Accessibility**: Large tap targets, easy keyboard nav.

## 2. Dashboard
- **Goal**: Show pending matches, upcoming swaps, earned credits.
- **Wireframe**: Card list + calendar peek.
- **Notes**: Color-blind friendly palette.

## 3. Matching Screen
- **Goal**: Browse potential matches by skill and proximity.
- **Wireframe**: Filter sidebar + map/list toggle.

## 4. Swap Detail & Chat
- **Goal**: Review partner’s profile, confirm swap time, chat.
- **Wireframe**: Split view: details above, chat thread below.

## 5. Feedback Screen
- **Goal**: Rate completed swap.
- **Wireframe**: Star selector + comment field.

> Wireframes can be delivered as JSON objects for tools like Figma API:
> ```json
> { "screen": "Dashboard", "elements": [ ... ] }
> ```
