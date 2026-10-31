# Organization Entity Design

## Purpose

Represents one company (tenant) using CapitalOS.

Every business entity belongs to exactly one organization.

---

## Fields

| Field | Type | Required | Notes |
|------|------|----------|------|
| id | UUID | Yes | Primary Key |
| legal_name | String | Yes | Registered company name |
| display_name | String | Yes | Display name in UI |
| registration_number | String | No | Company registration number |
| gst_number | String | No | GST registration |
| pan_number | String | No | PAN |
| email | String | Yes | Contact email |
| phone | String | No | Contact number |
| website | String | No | Website |
| timezone | String | Yes | Default: Asia/Kolkata |
| currency | String | Yes | Default: INR |
| country | String | Yes | Default: India |
| logo_url | String | No | Company logo |
| status | Enum | Yes | Active / Suspended |
| created_at | Timestamp | Yes | From TimestampMixin |
| updated_at | Timestamp | Yes | From TimestampMixin |

---

## Relationships

- Users
- Borrowers
- Investors
- Loans
- Payments
- Documents
- Audit Logs