from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .config import RAW_DIR


FIRST_NAMES = [
    "Aarav",
    "Aditi",
    "Ishaan",
    "Meera",
    "Rohan",
    "Anaya",
    "Vivaan",
    "Kavya",
    "Arjun",
    "Diya",
    "Neel",
    "Sara",
    "Reyansh",
    "Myra",
    "Krish",
    "Ira",
]

LAST_NAMES = [
    "Sharma",
    "Patel",
    "Verma",
    "Gupta",
    "Reddy",
    "Nair",
    "Kapoor",
    "Iyer",
    "Singh",
    "Joshi",
]

CITIES = ["Bengaluru", "Mumbai", "Delhi", "Pune", "Hyderabad", "Chennai", "Jaipur", "Ahmedabad"]
CHANNELS = ["Organic", "Paid Search", "Referral", "Social", "Affiliate", "Email"]
PAYMENT_METHODS = ["Card", "UPI", "NetBanking", "Wallet"]
ISSUE_TYPES = ["Shipping Delay", "Refund Request", "Product Quality", "Payment Issue", "Account Help"]
PRIORITIES = ["Low", "Medium", "High"]


@dataclass
class CustomerProfile:
    customer_id: str
    signup_date: date
    first_name: str
    last_name: str
    email: str
    city: str
    country: str
    acquisition_channel: str
    loyalty_state: str


def _weighted_choice(randomizer: random.Random, choices: list[tuple[str, float]]) -> str:
    labels = [label for label, _ in choices]
    weights = [weight for _, weight in choices]
    return randomizer.choices(labels, weights=weights, k=1)[0]


def _random_date(randomizer: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=randomizer.randint(0, (end - start).days))


def _write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_source_data(seed: int = 42) -> dict[str, int]:
    randomizer = random.Random(seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    signup_start = date(2024, 1, 1)
    signup_end = date(2025, 12, 15)
    analysis_end = date(2026, 3, 15)

    customers: list[CustomerProfile] = []
    customer_rows: list[dict[str, object]] = []

    for idx in range(1, 251):
        signup_date = _random_date(randomizer, signup_start, signup_end)
        first_name = randomizer.choice(FIRST_NAMES)
        last_name = randomizer.choice(LAST_NAMES)
        customer_id = f"C{idx:04d}"
        email = f"{first_name.lower()}.{last_name.lower()}{idx}@example.com"
        loyalty_state = _weighted_choice(
            randomizer,
            [
                ("new", 0.22),
                ("one_time", 0.30),
                ("repeat", 0.28),
                ("loyal", 0.15),
                ("at_risk", 0.05),
            ],
        )
        profile = CustomerProfile(
            customer_id=customer_id,
            signup_date=signup_date,
            first_name=first_name,
            last_name=last_name,
            email=email,
            city=randomizer.choice(CITIES),
            country="India",
            acquisition_channel=_weighted_choice(
                randomizer,
                [
                    ("Organic", 0.26),
                    ("Paid Search", 0.18),
                    ("Referral", 0.16),
                    ("Social", 0.22),
                    ("Affiliate", 0.08),
                    ("Email", 0.10),
                ],
            ),
            loyalty_state=loyalty_state,
        )
        customers.append(profile)
        customer_rows.append(
            {
                "customer_id": profile.customer_id,
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "email": profile.email,
                "city": profile.city,
                "country": profile.country,
                "signup_date": profile.signup_date.isoformat(),
                "acquisition_channel": profile.acquisition_channel,
            }
        )

    order_rows: list[dict[str, object]] = []
    payment_rows: list[dict[str, object]] = []
    support_rows: list[dict[str, object]] = []

    order_index = 1
    payment_index = 1
    ticket_index = 1

    for customer in customers:
        possible_days = max((analysis_end - customer.signup_date).days, 1)
        max_orders = {
            "new": randomizer.randint(0, 2),
            "one_time": 1,
            "repeat": randomizer.randint(2, 4),
            "loyal": randomizer.randint(5, 9),
            "at_risk": randomizer.randint(3, 6),
        }[customer.loyalty_state]

        order_dates: list[date] = []
        current_date = customer.signup_date + timedelta(days=randomizer.randint(1, min(20, possible_days)))

        for _ in range(max_orders):
            if current_date > analysis_end:
                break
            if customer.loyalty_state == "loyal":
                gap = randomizer.randint(18, 45)
            elif customer.loyalty_state == "repeat":
                gap = randomizer.randint(30, 75)
            elif customer.loyalty_state == "at_risk":
                gap = randomizer.randint(35, 65)
            else:
                gap = randomizer.randint(45, 120)
            order_dates.append(current_date)
            current_date += timedelta(days=gap)

        if customer.loyalty_state == "at_risk" and len(order_dates) >= 2:
            drift = randomizer.randint(120, 220)
            order_dates[-1] = min(order_dates[-2] + timedelta(days=drift), analysis_end - timedelta(days=30))

        for order_date in order_dates:
            gross_amount = round(randomizer.uniform(35, 450), 2)
            discount_amount = round(gross_amount * randomizer.choice([0, 0.05, 0.10, 0.15]), 2)
            shipping_fee = round(randomizer.choice([0, 0, 0, 4.99, 7.99]), 2)
            order_status = _weighted_choice(
                randomizer,
                [
                    ("completed", 0.83),
                    ("returned", 0.09),
                    ("cancelled", 0.08),
                ],
            )
            net_amount = round(max(gross_amount - discount_amount + shipping_fee, 0), 2)
            order_id = f"O{order_index:05d}"
            order_index += 1

            order_rows.append(
                {
                    "order_id": order_id,
                    "customer_id": customer.customer_id,
                    "order_date": order_date.isoformat(),
                    "order_status": order_status,
                    "gross_amount": gross_amount,
                    "discount_amount": discount_amount,
                    "shipping_fee": shipping_fee,
                    "net_amount": net_amount,
                    "items_count": randomizer.randint(1, 6),
                }
            )

            if order_status == "completed":
                payment_status = "paid"
                refunded_amount = 0.0
            elif order_status == "returned":
                payment_status = _weighted_choice(
                    randomizer,
                    [("refunded", 0.65), ("partially_refunded", 0.35)],
                )
                refunded_amount = net_amount if payment_status == "refunded" else round(net_amount * randomizer.uniform(0.3, 0.8), 2)
            else:
                payment_status = _weighted_choice(randomizer, [("failed", 0.6), ("refunded", 0.4)])
                refunded_amount = net_amount if payment_status == "refunded" else 0.0

            payment_rows.append(
                {
                    "payment_id": f"P{payment_index:05d}",
                    "order_id": order_id,
                    "payment_date": (order_date + timedelta(days=randomizer.randint(0, 3))).isoformat(),
                    "payment_method": randomizer.choice(PAYMENT_METHODS),
                    "payment_status": payment_status,
                    "amount": net_amount,
                    "refunded_amount": round(refunded_amount, 2),
                }
            )
            payment_index += 1

            if order_status != "completed" or randomizer.random() < 0.22:
                ticket_count = 1 if randomizer.random() < 0.8 else 2
                for _ in range(ticket_count):
                    issue_type = _weighted_choice(
                        randomizer,
                        [
                            ("Shipping Delay", 0.28),
                            ("Refund Request", 0.22),
                            ("Product Quality", 0.18),
                            ("Payment Issue", 0.17),
                            ("Account Help", 0.15),
                        ],
                    )
                    priority = _weighted_choice(
                        randomizer,
                        [("Low", 0.35), ("Medium", 0.45), ("High", 0.20)],
                    )
                    resolution_hours = round(
                        randomizer.uniform(2, 12)
                        if priority == "Low"
                        else randomizer.uniform(8, 30)
                        if priority == "Medium"
                        else randomizer.uniform(18, 72),
                        1,
                    )
                    csat_score = max(
                        1,
                        min(
                            5,
                            int(
                                round(
                                    4.8
                                    - (resolution_hours / 40)
                                    - (1 if order_status != "completed" else 0)
                                    - (0.4 if issue_type == "Refund Request" else 0)
                                    + randomizer.uniform(-0.7, 0.7)
                                )
                            ),
                        ),
                    )
                    support_rows.append(
                        {
                            "ticket_id": f"T{ticket_index:05d}",
                            "customer_id": customer.customer_id,
                            "order_id": order_id,
                            "created_at": (order_date + timedelta(days=randomizer.randint(1, 10))).isoformat(),
                            "issue_type": issue_type,
                            "priority": priority,
                            "resolution_hours": resolution_hours,
                            "csat_score": csat_score,
                            "ticket_status": "resolved",
                        }
                    )
                    ticket_index += 1

        if not order_dates and randomizer.random() < 0.18:
            support_rows.append(
                {
                    "ticket_id": f"T{ticket_index:05d}",
                    "customer_id": customer.customer_id,
                    "order_id": "",
                    "created_at": (customer.signup_date + timedelta(days=randomizer.randint(3, 45))).isoformat(),
                    "issue_type": "Account Help",
                    "priority": randomizer.choice(PRIORITIES),
                    "resolution_hours": round(randomizer.uniform(1.5, 18), 1),
                    "csat_score": randomizer.randint(3, 5),
                    "ticket_status": "resolved",
                }
            )
            ticket_index += 1

    _write_csv(
        RAW_DIR / "customers.csv",
        customer_rows,
        ["customer_id", "first_name", "last_name", "email", "city", "country", "signup_date", "acquisition_channel"],
    )
    _write_csv(
        RAW_DIR / "orders.csv",
        order_rows,
        ["order_id", "customer_id", "order_date", "order_status", "gross_amount", "discount_amount", "shipping_fee", "net_amount", "items_count"],
    )
    _write_csv(
        RAW_DIR / "payments.csv",
        payment_rows,
        ["payment_id", "order_id", "payment_date", "payment_method", "payment_status", "amount", "refunded_amount"],
    )
    _write_csv(
        RAW_DIR / "support_tickets.csv",
        support_rows,
        ["ticket_id", "customer_id", "order_id", "created_at", "issue_type", "priority", "resolution_hours", "csat_score", "ticket_status"],
    )

    return {
        "customers": len(customer_rows),
        "orders": len(order_rows),
        "payments": len(payment_rows),
        "support_tickets": len(support_rows),
    }

