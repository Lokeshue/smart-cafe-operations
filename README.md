# Smart Café Operations & Nutrition Tracker

A full-stack portfolio project built for a **Starbucks Software Engineer** interview. It solves two real in-store problems: giving customers live nutrition feedback while customizing drinks, and giving baristas a smarter order queue during rush hours.

---

## Problem Statement

**For customers:** When customizing a drink (milk type, syrups, size, add-ons), nutrition information is often unclear until after ordering. Customers want to see calories, sugar, protein, and caffeine update in real time.

**For baristas:** During rush hours, orders arrive from mobile, drive-thru, and walk-in channels simultaneously. Baristas need intelligent prioritization — older orders first, drive-thru boosted when waits are long, and similar drinks batched together — plus visibility into demand surges.

---

## Solution Overview

This app provides:

1. **Customer Drink Customizer** — Select a base drink, customize milk/syrups/size/add-ons, and see live nutrition updates instantly.
2. **Smart Barista Queue** — A prioritized dashboard showing all active orders with channel, status, priority score, and one-click status progression.
3. **Operations Analytics** — Monitor total orders, average wait time, orders by channel, and rush alerts.

---

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | Next.js 15, React 19, TypeScript    |
| Styling    | Tailwind CSS                        |
| Backend    | FastAPI (Python)                    |
| Database   | SQLite + SQLAlchemy ORM             |
| Validation | Pydantic v2                         |

---

## Features

### Customer Side
- Drink customization page with 5 base drinks (Latte, Cold Brew, Frappuccino, Matcha, Refresher)
- Customize milk type, syrup pumps, size, and add-ons
- **Live nutrition tracker** — calories, sugar, protein, caffeine update on every change
- Nutrition summary: *"Your customized drink has X calories, Y grams sugar, Z grams protein."*
- Place orders via mobile, drive-thru, or walk-in
- See queue position and estimated wait time after ordering

### Barista Side
- Order queue dashboard with smart sequencing
- Orders from mobile, drive-thru, and walk-in channels
- Each order shows: customer name, drink, customizations, channel, time, priority score, status
- Status flow: Received → In Progress → Ready → Picked Up
- **Smart sequencing:** age priority, drive-thru boost, drink batching
- **Rush alert:** "Rush detected: 12 orders in 10 minutes"
- Auto-refresh every 5 seconds

### Analytics Dashboard
- Total orders, active queue size, average wait time
- Orders by channel breakdown
- Rush alert status

---

## Project Structure

```
Starbucks/
├── README.md
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── cafe.db              # Created on first run
│   └── app/
│       ├── main.py           # FastAPI entry point
│       ├── database.py       # SQLite setup
│       ├── models.py         # ORM models
│       ├── schemas.py        # Pydantic validation
│       ├── seed_data.py      # Sample drinks & orders
│       ├── routers/
│       │   ├── drinks.py
│       │   ├── orders.py
│       │   └── analytics.py
│       └── services/
│           ├── nutrition.py  # Live nutrition calculation
│           ├── queue.py      # Smart queue sequencing
│           └── analytics.py  # Dashboard metrics
└── frontend/
    ├── package.json
    ├── tailwind.config.ts
    └── src/
        ├── app/
        │   ├── page.tsx          # Landing page
        │   ├── customize/page.tsx
        │   ├── barista/page.tsx
        │   └── analytics/page.tsx
        ├── components/
        └── lib/api.ts            # API client
```

---

## API Endpoints

| Method | Endpoint                    | Description                              |
|--------|-----------------------------|------------------------------------------|
| GET    | `/api/drinks`               | List all base drinks                     |
| POST   | `/api/customize-drink`      | Calculate nutrition for customization    |
| POST   | `/api/orders`               | Place a new order                        |
| GET    | `/api/orders`               | List all orders (optional `?status=`)    |
| GET    | `/api/orders/{id}`          | Get single order with queue position     |
| PATCH  | `/api/orders/{id}/status`   | Update order status                      |
| GET    | `/api/queue/status`         | Smart-sequenced queue + rush alert       |
| GET    | `/api/analytics/rush`       | Rush detection analytics                 |
| GET    | `/api/analytics/dashboard`  | Full operations dashboard                |
| GET    | `/health`                   | Health check                             |
| GET    | `/docs`                     | Interactive Swagger UI                     |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd Starbucks
```

### 2. Start the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000** with interactive docs at **http://localhost:8000/docs**.

On first run, SQLite creates `cafe.db` and seeds sample drinks, ingredients, and orders.

### 3. Start the frontend

In a new terminal:

```bash
cd frontend
npm install
cp .env.local.example .env.local   # optional — defaults to localhost:8000
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## Screenshots

> _Add screenshots here after running locally:_
>
> - Home page
> - Drink customization with live nutrition
> - Barista queue dashboard
> - Analytics dashboard

---

## How This Aligns with the Starbucks Software Engineer Role

| Skill Area              | Demonstrated In This Project                              |
|-------------------------|-----------------------------------------------------------|
| **API Design**          | RESTful endpoints with validation, error handling, docs  |
| **Customer Experience** | Live nutrition transparency — a core mobile app feature    |
| **Store Operations**    | Smart queue sequencing for multi-channel order fulfillment |
| **Data & Analytics**    | Rush detection, wait time metrics, channel breakdown       |
| **Full-Stack Delivery** | End-to-end feature from database to UI                     |
| **Code Quality**        | Clean architecture, typed schemas, logging, comments       |

This project mirrors real problems Starbucks engineering teams solve: mobile ordering nutrition data, drive-thru prioritization, and peak-hour operational tooling.

---

## Future Improvements

- **AWS Deployment** — Deploy backend on ECS/Lambda and frontend on Amplify or S3 + CloudFront
- **Real-time WebSocket Queue Updates** — Push queue changes to barista screens instantly instead of polling
- **Authentication** — Customer accounts and barista role-based access (OAuth / JWT)
- **CI/CD Pipeline** — GitHub Actions for lint, test, and deploy on merge
- **CloudWatch Monitoring** — Structured logging, metrics, and alerts for rush detection in production
- **Mobile App** — React Native client sharing the same API
- **Integration Tests** — pytest for backend, Playwright for frontend E2E

---

## License

MIT — Built as a portfolio project for interview purposes.
