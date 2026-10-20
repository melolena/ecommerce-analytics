# Initial Analytics Results

These results were generated from the local SQLite staging database with the rules in `business_rules.md`. They describe the historical Olist dataset and are not current market estimates.

## Delivered sales

Sales measures include orders with `order_status = 'delivered'` only. Item revenue and freight are calculated from order items and kept separate; payment values are not added to them.

| Measure | Result |
|---|---:|
| Delivered orders | 96,478 |
| Item revenue | R$ 13,221,498.11 |
| Freight value | R$ 2,198,275.64 |
| Order value (items plus freight) | R$ 15,419,773.75 |
| Average delivered order value | R$ 159.83 |

Monthly results use `order_purchase_timestamp`. The latest month with delivered orders is August 2018, while source purchase timestamps extend into October 2018. Review late-period completeness before interpreting the end of the trend.

## Delivery and reviews

- 96,470 delivered orders have both delivery timestamps required for the on-time calculation; 8 delivered orders lack the customer-delivery timestamp and are excluded from its denominator.
- 89,936 eligible deliveries were on time and 6,534 were late, for an on-time delivery rate of **93.23%**.
- After averaging review scores per order, mean scores were **4.29** for on-time deliveries and **2.27** for late deliveries. This is a descriptive relationship and does not establish causation.

## Other initial breakdowns

- **Payment method:** credit card appeared on 74,304 delivered orders, boleto on 19,191, voucher on 3,679, and debit card on 1,485. A delivered order can use more than one payment method, so these order counts are not additive. Payment value remains separate from sales value.
- **Product category:** `health_beauty` had the highest delivered item revenue at R$ 1,233,131.72. The query uses English translations where available, Portuguese source names for untranslated categories, and `(missing category)` for missing source categories.
- **Customer state:** SP had the highest delivered item revenue at R$ 5,067,633.16. State refers to the customer/buyer, not the seller.
- **Repeat customers:** 2,801 of 93,358 identifiable customers with at least one delivered order had two or more delivered orders during the full dataset period: **3.00%**.

## Limits and open decisions

- Data are historical, with purchase timestamps from 2016-09-04 through 2018-10-17.
- Repeat-customer rate uses delivered orders only and the full dataset period, as defined in `business_rules.md`.
- Source timestamps have no explicit timezone; they are used as provided without conversion. Delivery timing compares calendar dates.
- The results depend on the documented local preparation rules and should be rerun if those rules or source files change.
