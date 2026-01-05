# React Migration Plan: Ancla Capital

## Overview

This document outlines the migration strategy from Flask/Jinja2 server-rendered templates to a React SPA frontend with a Flask REST API backend.

## Current Architecture

- **Backend**: Flask 2.3.1 with SQLAlchemy ORM
- **Frontend**: Jinja2 templates (31 templates), custom CSS (537 lines), minimal vanilla JS
- **Database**: PostgreSQL with GeoAlchemy2
- **Authentication**: Flask-Login with session cookies

## Target Architecture

```
ancla/
├── app/                        # Flask Backend (existing, refactored)
│   ├── api/                    # NEW: REST API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py            # JWT authentication endpoints
│   │   ├── loans.py           # Loan CRUD API
│   │   ├── borrowers.py       # Borrower API
│   │   ├── payments.py        # Payment API
│   │   ├── properties.py      # Property/collateral API
│   │   ├── collections.py     # Collections API
│   │   ├── documents.py       # Legal documents API
│   │   └── dashboard.py       # Dashboard metrics API
│   ├── schemas/               # NEW: Marshmallow/Pydantic serialization
│   ├── models/                # KEEP: Existing SQLAlchemy models
│   ├── services/              # KEEP: Existing business logic
│   ├── blueprints/            # DEPRECATE: Phase out after migration
│   └── templates/             # DEPRECATE: Phase out after migration
│
├── frontend/                   # NEW: React Application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   │   ├── ui/            # Base components (Button, Card, Input, etc.)
│   │   │   ├── layout/        # Layout components (Navbar, Sidebar, Page)
│   │   │   ├── forms/         # Form components
│   │   │   └── data/          # Data display (Table, Badge, Currency)
│   │   ├── pages/             # Route-level page components
│   │   │   ├── auth/          # Login, Register, ForgotPassword
│   │   │   ├── dashboard/     # Dashboard page
│   │   │   ├── loans/         # Loan list, detail, form
│   │   │   ├── borrowers/     # Borrower management
│   │   │   ├── payments/      # Payment recording
│   │   │   ├── properties/    # Property/collateral management
│   │   │   ├── collections/   # Collections workflow
│   │   │   └── legal/         # Document management
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API client functions
│   │   ├── store/             # Zustand state management
│   │   ├── types/             # TypeScript interfaces
│   │   ├── lib/               # Utilities and helpers
│   │   └── styles/            # Global styles
│   ├── public/                # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── tailwind.config.js
```

## Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Framework** | React 18 | Industry standard, large ecosystem |
| **Language** | TypeScript | Type safety, better IDE support |
| **Bundler** | Vite | Fast builds, excellent DX |
| **Routing** | React Router v6 | Standard routing solution |
| **Server State** | TanStack Query v5 | Caching, background updates, optimistic UI |
| **Client State** | Zustand | Lightweight, simple API |
| **Forms** | React Hook Form + Zod | Performant validation |
| **UI Components** | Custom + Tailwind CSS | Match existing design system |
| **HTTP Client** | Axios | Interceptors, error handling |
| **Auth** | JWT (access + refresh tokens) | Stateless, scalable |
| **Testing** | Vitest + Testing Library | Fast, React-focused |

## Migration Phases

### Phase 1: Foundation (Current)
**Goal**: Set up React project structure and core infrastructure

- [x] Create frontend directory with Vite + TypeScript + React
- [x] Configure Tailwind CSS with existing color palette
- [x] Create base UI components matching current design
- [x] Set up routing structure
- [x] Create API client with interceptors
- [x] Implement authentication context and hooks
- [x] Build layout components (Navbar, PageLayout)

### Phase 2: Flask API Layer
**Goal**: Create REST API endpoints parallel to existing routes

- [ ] Install Flask-JWT-Extended for JWT auth
- [ ] Create `app/api/` blueprint structure
- [ ] Create Marshmallow schemas for serialization
- [ ] Implement auth endpoints (login, register, refresh, logout)
- [ ] Implement dashboard metrics endpoint
- [ ] Implement borrowers CRUD endpoints
- [ ] Implement properties CRUD endpoints
- [ ] Implement loans CRUD endpoints
- [ ] Implement payments CRUD endpoints
- [ ] Implement collections endpoints
- [ ] Implement documents endpoints
- [ ] Add API documentation (OpenAPI/Swagger)

### Phase 3: Core Pages Migration
**Goal**: Migrate essential pages to React

- [ ] Authentication pages (Login, Register, Forgot Password)
- [ ] Dashboard with real-time metrics
- [ ] Loan list with filtering and sorting
- [ ] Loan detail view
- [ ] Loan creation form with live calculations
- [ ] Borrower list and detail views
- [ ] Property list and detail views

### Phase 4: Workflow Pages
**Goal**: Migrate business workflow pages

- [ ] Payment recording with schedule view
- [ ] Payment history and overdue dashboard
- [ ] Collections workflow pages
- [ ] Legal document management
- [ ] Loan approval workflow
- [ ] Borrower portal (my loans view)

### Phase 5: Advanced Features
**Goal**: Add enhanced functionality

- [ ] Real-time notifications (WebSocket)
- [ ] Optimistic updates for better UX
- [ ] Offline support with service workers
- [ ] Export functionality (PDF, Excel)
- [ ] Advanced reporting dashboards
- [ ] Mobile-responsive optimizations

### Phase 6: Cleanup & Deployment
**Goal**: Finalize migration and remove legacy code

- [ ] Remove Jinja2 templates
- [ ] Remove Flask-Login dependencies
- [ ] Update deployment configuration
- [ ] Performance optimization
- [ ] Security audit
- [ ] Documentation updates

## Component Mapping

### Templates to React Components

| Jinja2 Template | React Component | Priority |
|-----------------|-----------------|----------|
| `base.html` | `Layout.tsx` | P1 |
| `auth/login.html` | `pages/auth/Login.tsx` | P1 |
| `auth/register.html` | `pages/auth/Register.tsx` | P1 |
| `admin/dashboard.html` | `pages/dashboard/Dashboard.tsx` | P1 |
| `loans/index.html` | `pages/loans/LoanList.tsx` | P1 |
| `loans/view.html` | `pages/loans/LoanDetail.tsx` | P1 |
| `loans/form.html` | `pages/loans/LoanForm.tsx` | P1 |
| `borrowers/index.html` | `pages/borrowers/BorrowerList.tsx` | P2 |
| `borrowers/view.html` | `pages/borrowers/BorrowerDetail.tsx` | P2 |
| `borrowers/form.html` | `pages/borrowers/BorrowerForm.tsx` | P2 |
| `collateral/index.html` | `pages/properties/PropertyList.tsx` | P2 |
| `collateral/view.html` | `pages/properties/PropertyDetail.tsx` | P2 |
| `payments/index.html` | `pages/payments/PaymentList.tsx` | P2 |
| `payments/record.html` | `pages/payments/RecordPayment.tsx` | P2 |
| `collections/index.html` | `pages/collections/CollectionList.tsx` | P3 |
| `legal/index.html` | `pages/legal/DocumentList.tsx` | P3 |

### Reusable Components

| Component | Used By | Features |
|-----------|---------|----------|
| `Button` | All pages | Variants, sizes, loading state |
| `Card` | All pages | Header, body, actions slots |
| `Input` | All forms | Validation, error display |
| `Select` | All forms | Options, search, clear |
| `DataTable` | List pages | Sorting, filtering, pagination |
| `StatusBadge` | Loans, borrowers, documents | Color-coded status display |
| `Currency` | Financial displays | Q format, color for negative |
| `Modal` | Confirmations, quick actions | Header, body, footer |
| `Alert` | Notifications | Variants, dismissible |
| `PageHeader` | All pages | Title, breadcrumbs, actions |

## API Endpoint Design

### Authentication

```
POST   /api/auth/login          # Get access + refresh tokens
POST   /api/auth/register       # Create account
POST   /api/auth/refresh        # Refresh access token
POST   /api/auth/logout         # Invalidate tokens
POST   /api/auth/forgot-password
POST   /api/auth/reset-password
GET    /api/auth/me             # Current user profile
```

### Resources

```
# Loans
GET    /api/loans               # List with filters
POST   /api/loans               # Create loan
GET    /api/loans/:id           # Get loan detail
PUT    /api/loans/:id           # Update loan
POST   /api/loans/:id/approve   # Approve loan
POST   /api/loans/:id/activate  # Activate/disburse loan
GET    /api/loans/:id/schedule  # Payment schedule
GET    /api/loans/:id/payments  # Payment history

# Borrowers
GET    /api/borrowers           # List
POST   /api/borrowers           # Create
GET    /api/borrowers/:id       # Detail
PUT    /api/borrowers/:id       # Update
POST   /api/borrowers/:id/verify

# Properties
GET    /api/properties
POST   /api/properties
GET    /api/properties/:id
PUT    /api/properties/:id
POST   /api/properties/:id/verify

# Payments
GET    /api/payments
POST   /api/payments            # Record payment
GET    /api/payments/overdue

# Collections
GET    /api/collections/delinquent
POST   /api/collections/:loan_id/action

# Documents
GET    /api/documents
POST   /api/documents/:id/upload
POST   /api/documents/:id/accept

# Dashboard
GET    /api/dashboard/metrics
GET    /api/dashboard/portfolio
```

## Design System

### Colors (from existing CSS variables)

```css
--primary: #1a365d      /* Navy blue - main brand */
--primary-light: #2c5282
--secondary: #2563eb    /* Blue - actions */
--success: #059669      /* Green - positive */
--warning: #d97706      /* Orange - caution */
--danger: #dc2626       /* Red - error/negative */
--info: #0284c7         /* Light blue - info */
```

### Status Colors

| Status | Background | Text |
|--------|------------|------|
| Draft | gray-200 | gray-700 |
| Under Review | blue-100 | blue-800 |
| Approved | green-100 | green-800 |
| Active | green-200 | green-900 |
| Matured | amber-100 | amber-800 |
| Defaulted | red-100 | red-800 |
| Legal Ready | pink-100 | pink-800 |
| Closed | gray-300 | gray-700 |

## File Structure Details

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Select.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Alert.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Spinner.tsx
│   │   │   └── index.ts
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── PageLayout.tsx
│   │   │   ├── PageHeader.tsx
│   │   │   └── index.ts
│   │   ├── forms/
│   │   │   ├── FormField.tsx
│   │   │   ├── FormSelect.tsx
│   │   │   ├── FormTextarea.tsx
│   │   │   └── index.ts
│   │   └── data/
│   │       ├── DataTable.tsx
│   │       ├── StatusBadge.tsx
│   │       ├── Currency.tsx
│   │       ├── EmptyState.tsx
│   │       └── index.ts
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   └── ForgotPassword.tsx
│   │   ├── dashboard/
│   │   │   └── Dashboard.tsx
│   │   ├── loans/
│   │   │   ├── LoanList.tsx
│   │   │   ├── LoanDetail.tsx
│   │   │   └── LoanForm.tsx
│   │   ├── borrowers/
│   │   ├── payments/
│   │   ├── properties/
│   │   ├── collections/
│   │   └── legal/
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useLoans.ts
│   │   ├── useBorrowers.ts
│   │   └── useToast.ts
│   ├── services/
│   │   ├── api.ts           # Axios instance
│   │   ├── auth.ts          # Auth API calls
│   │   ├── loans.ts         # Loan API calls
│   │   ├── borrowers.ts
│   │   ├── payments.ts
│   │   └── properties.ts
│   ├── store/
│   │   ├── authStore.ts     # Auth state (Zustand)
│   │   └── uiStore.ts       # UI state (sidebar, modals)
│   ├── types/
│   │   ├── auth.ts
│   │   ├── loan.ts
│   │   ├── borrower.ts
│   │   ├── payment.ts
│   │   └── index.ts
│   ├── lib/
│   │   ├── utils.ts         # Utility functions
│   │   ├── constants.ts     # App constants
│   │   └── formatters.ts    # Currency, date formatters
│   ├── styles/
│   │   └── globals.css      # Tailwind + custom styles
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── public/
│   └── logo.png
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

## Success Metrics

- [ ] All 31 templates migrated to React components
- [ ] 100% feature parity with existing application
- [ ] Sub-100ms navigation between pages
- [ ] Mobile-responsive on all pages
- [ ] 80%+ test coverage on components
- [ ] Lighthouse performance score > 90
- [ ] No regressions in functionality

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Learning curve for team | Medium | Pair programming, documentation |
| Feature regression | High | Comprehensive testing, parallel deployment |
| Extended timeline | Medium | Phased approach, MVP first |
| API security issues | High | Security audit, JWT best practices |
| Browser compatibility | Low | Polyfills, modern baseline |

## Next Steps

1. Complete Phase 1 foundation setup
2. Begin Flask API development in parallel
3. Implement authentication flow end-to-end
4. Build dashboard as proof of concept
5. Iterate through remaining pages by priority
