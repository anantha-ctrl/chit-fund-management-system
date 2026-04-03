# Implementation Plan: Core Financial Features

This plan outlines the steps to implement advanced financial logic including foreman commissions, automated dividends, penalty calculations, and guarantor tracking.

## 1. Model Enhancements

| App | Model | Changes |
| :--- | :--- | :--- |
| **chits** | `ChitGroup` | Add `commission_percentage` (Decimal, default 5.00). |
| **auctions** | `Auction` | Add `foreman_commission`, `total_dividend`, `dividend_per_member`. |
| **payments** | `Payment` | Add `due_date`, `penalty_amount`, `dividend_amount`. |
| **auctions** | `Guarantor` | **New Model**: `auction` (FK), `name`, `phone`, `id_proof`. |

## 2. Logic Implementation

### A. Dividend Distribution (Automated)
When an `Auction` is saved:
1.  **Total Discount** = `bid_amount`.
2.  **Foreman Commission** = (`commission_percentage` / 100) * `chit_amount`.
3.  **Total Dividend** = `Total Discount` - `Foreman Commission`.
4.  **Dividend Per Member** = `Total Dividend` / `Total Members`.
5.  **Payment Adjustment**: Create or update the next month's `Payment` objects for all members with the `dividend_amount` subtracted from the base installment.

### B. Auto-Penalty Logic
A management command `calculate_penalties` will:
1.  Filter `Payment` where `status` is `PENDING` and `due_date` < `today`.
2.  Apply penalty (e.g., 2% of installment or fixed daily rate).
3.  Update `penalty_amount` in `Payment` and sync with `Settlement`.

### C. Guarantor Workflow
1.  Admin selects a winner in an Auction.
2.  Admin must upload/fill 2-3 Guarantor details before the "Winner Payout" is marked as "Released".

## 3. Implementation Steps

### Done
- [ ] Update `chits/models.py`
- [ ] Update `auctions/models.py` (Add fields + calculation logic)
- [ ] Update `payments/models.py` (Add penalty fields)
- [ ] Create `Guarantor` model
- [ ] Implement `calculate_penalties` management command
- [ ] Update Views & Templates for Auctions to show Dividend info
- [ ] Update Settlement logic to include these new fields
