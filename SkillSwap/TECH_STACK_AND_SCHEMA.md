# Tech Stack & API

backend:
  framework: Node.js + Express
  db: MongoDB (Atlas)
  auth: Firebase Auth (email+OAuth)
  messaging: Socket.io

frontend:
  framework: React Native (iOS/Android) + React Web
  styling: Tailwind CSS

---

# API Endpoints

- `POST /api/signup`
- `POST /api/login`
- `GET  /api/users/:id/matches`
- `POST /api/swaps`
- `GET  /api/swaps/:id/messages`
- `POST /api/swaps/:id/feedback`

---

# Database Schema

users:
  - _id: ObjectId
  - name: String
  - skills: [String]
  - avail: [{ day, start, end }]
  - reputation: Number

swaps:
  - _id: ObjectId
  - participants: [ObjectId]
  - type: enum{PAIR,CHAIN}
  - start: Date
  - end: Date
  - status: enum{PENDING,CONFIRMED,COMPLETED}

messages:
  - _id: ObjectId
  - swapId: ObjectId
  - sender: ObjectId
  - text: String
  - timestamp: Date

feedback:
  - _id: ObjectId
  - swapId: ObjectId
  - rater: ObjectId
  - rating: Number
  - comment: String
