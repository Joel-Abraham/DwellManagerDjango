"""
DwellManager — Development Seed Data
Run: python seed_django.py
"""
import os
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dwellmanager.settings")
django.setup()

from django.utils import timezone
from api.models import (
    Flat, Resident, MaintenanceRequest, Payment, Visitor,
    UserRole, MaintenanceStatus, PaymentStatus, VisitorStatus,
    MaintenanceCategory, ChargeType, ResidentStatus, VehicleType,
)


def seed():
    print("🏗  Seeding database...")

    # ── FLATS ────────────────────────────────────────────
    flats_data = [
        # (flat_number, block, floor, flat_type, owner_name, base_maintenance)
        ("A-101", "Block A", 1, "2BHK", "Rahul Sharma",   Decimal("8000.00")),
        ("A-102", "Block A", 1, "3BHK", "Priya Patel",    Decimal("12000.00")),
        ("A-201", "Block A", 2, "3BHK", "Amit Kumar",     Decimal("12500.00")),
        ("B-101", "Block B", 1, "2BHK", "Sneha Reddy",    Decimal("8500.00")),
        ("B-102", "Block B", 1, "1BHK", "Vikram Singh",   Decimal("6000.00")),
        ("B-201", "Block B", 2, "4BHK", "Deepa Nair",     Decimal("18000.00")),
    ]

    flats = {}
    for f_num, block, floor, f_type, owner, amount in flats_data:
        flat, _ = Flat.objects.get_or_create(
            flat_number=f_num,
            block=block,
            defaults={
                "floor": floor,
                "flat_type": f_type,
                "owner_name": owner,
                "base_maintenance_amount": amount,
            },
        )
        flats[f_num] = flat
    print(f"   ✓ {len(flats)} flats created")

    # ── ADMIN ────────────────────────────────────────────
    if not Resident.objects.filter(username="admin").exists():
        Resident.objects.create_superuser(
            username="admin",
            password="admin123",
            full_name="System Admin",
            role=UserRole.ADMIN,
            contact_number="0000000000",
        )
        print("   ✓ Admin created (admin / admin123)")

    # ── GUARD ────────────────────────────────────────────
    if not Resident.objects.filter(username="guard1").exists():
        Resident.objects.create_user(
            username="guard1",
            password="guard123",
            full_name="Ramesh Guard",
            role=UserRole.GUARD,
            contact_number="9999999999",
        )
        print("   ✓ Guard created (guard1 / guard123)")

    # ── RESIDENTS ────────────────────────────────────────
    if not Resident.objects.filter(username="resident1").exists():
        Resident.objects.create_user(
            username="resident1",
            password="resident123",
            full_name="Arjun Mehta",
            role=UserRole.RESIDENT,
            flat=flats["A-101"],
            contact_number="9876543210",
            email="arjun@example.com",
            move_in_date=date(2024, 6, 1),
            status=ResidentStatus.ACTIVE,
        )
        print("   ✓ Resident 1 created (resident1 / resident123) → A-101")

    if not Resident.objects.filter(username="resident2").exists():
        Resident.objects.create_user(
            username="resident2",
            password="resident123",
            full_name="Kavitha Rao",
            role=UserRole.RESIDENT,
            flat=flats["B-101"],
            contact_number="9876543211",
            email="kavitha@example.com",
            move_in_date=date(2025, 1, 15),
            status=ResidentStatus.ACTIVE,
        )
        print("   ✓ Resident 2 created (resident2 / resident123) → B-101")

    if not Resident.objects.filter(username="resident3").exists():
        Resident.objects.create_user(
            username="resident3",
            password="resident123",
            full_name="Sunil Verma",
            role=UserRole.RESIDENT,
            flat=flats["A-201"],
            contact_number="9876543212",
            email="sunil@example.com",
            move_in_date=date(2023, 3, 10),
            status=ResidentStatus.INACTIVE,
        )
        print("   ✓ Resident 3 created (resident3 / resident123) → A-201 [Inactive]")

    if not Resident.objects.filter(username="resident4").exists():
        Resident.objects.create_user(
            username="resident4",
            password="resident123",
            full_name="Meera Joshi",
            role=UserRole.RESIDENT,
            flat=flats["B-102"],
            contact_number="9876543213",
            email="meera@example.com",
            move_in_date=date(2022, 11, 1),
            status=ResidentStatus.MOVED_OUT,
        )
        print("   ✓ Resident 4 created (resident4 / resident123) → B-102 [Moved-out]")

    # ── MAINTENANCE REQUESTS ─────────────────────────────
    # Pending request for A-101
    mr1, _ = MaintenanceRequest.objects.get_or_create(
        flat=flats["A-101"],
        category=MaintenanceCategory.PLUMBING,
        description="Kitchen tap is leaking heavily. Water wastage.",
        defaults={"status": MaintenanceStatus.PENDING},
    )

    # Assigned request for B-101 (with fee)
    mr2, _ = MaintenanceRequest.objects.get_or_create(
        flat=flats["B-101"],
        category=MaintenanceCategory.ELECTRICAL,
        description="Living room socket sparks when plugged in.",
        defaults={
            "status": MaintenanceStatus.ASSIGNED,
            "assigned_to": "Electrician Bob",
            "scheduled_date": date(2026, 10, 15),
            "fee_amount": Decimal("250.00"),
        },
    )

    # In Progress request for A-101
    mr3, _ = MaintenanceRequest.objects.get_or_create(
        flat=flats["A-101"],
        category=MaintenanceCategory.HVAC,
        description="Bedroom AC blowing warm air, needs gas refill.",
        defaults={
            "status": MaintenanceStatus.IN_PROGRESS,
            "assigned_to": "CoolTech Services",
            "scheduled_date": date(2026, 9, 20),
            "fee_amount": Decimal("1500.00"),
        },
    )

    # Completed request for A-101
    mr4, _ = MaintenanceRequest.objects.get_or_create(
        flat=flats["A-101"],
        category=MaintenanceCategory.PAINTING,
        description="Wall paint peeling in hallway.",
        defaults={
            "status": MaintenanceStatus.COMPLETED,
            "assigned_to": "PaintPro Ltd",
            "scheduled_date": date(2026, 8, 10),
            "fee_amount": Decimal("500.00"),
        },
    )
    print(f"   ✓ Maintenance requests seeded")

    # ── PAYMENTS / BILLING ───────────────────────────────
    # Base Maintenance — A-101 — Unpaid (September 2026)
    Payment.objects.get_or_create(
        flat=flats["A-101"],
        charge_type=ChargeType.BASE_MAINTENANCE,
        billing_month="September 2026",
        defaults={
            "amount": flats["A-101"].base_maintenance_amount,
            "description": "Monthly Maintenance — September 2026",
            "status": PaymentStatus.UNPAID,
        },
    )

    # Base Maintenance — A-101 — Paid (August 2026)
    Payment.objects.get_or_create(
        flat=flats["A-101"],
        charge_type=ChargeType.BASE_MAINTENANCE,
        billing_month="August 2026",
        defaults={
            "amount": flats["A-101"].base_maintenance_amount,
            "description": "Monthly Maintenance — August 2026",
            "status": PaymentStatus.PAID,
            "payment_method": "UPI",
            "paid_at": timezone.now(),
            "receipt_ref": "RCPT-A101-AUG2026",
        },
    )

    # Additional Charge — A-101 — from painting request (Paid)
    Payment.objects.get_or_create(
        flat=flats["A-101"],
        charge_type=ChargeType.ADDITIONAL_CHARGE,
        source_request=mr4,
        defaults={
            "billing_month": "August 2026",
            "amount": Decimal("500.00"),
            "description": f"Maintenance Fee – (Request #{mr4.pk})",
            "status": PaymentStatus.PAID,
            "payment_method": "Net Banking",
            "paid_at": timezone.now(),
            "receipt_ref": "RCPT-A101-MNT-PAINT",
        },
    )

    # Additional Charge — A-101 — from HVAC request (Unpaid)
    Payment.objects.get_or_create(
        flat=flats["A-101"],
        charge_type=ChargeType.ADDITIONAL_CHARGE,
        source_request=mr3,
        defaults={
            "billing_month": "September 2026",
            "amount": Decimal("1500.00"),
            "description": f"Maintenance Fee – (Request #{mr3.pk})",
            "status": PaymentStatus.UNPAID,
        },
    )

    # Base Maintenance — B-101 — Unpaid (September 2026)
    Payment.objects.get_or_create(
        flat=flats["B-101"],
        charge_type=ChargeType.BASE_MAINTENANCE,
        billing_month="September 2026",
        defaults={
            "amount": flats["B-101"].base_maintenance_amount,
            "description": "Monthly Maintenance — September 2026",
            "status": PaymentStatus.UNPAID,
        },
    )

    # Additional Charge — B-101 — from electrical request (Unpaid)
    Payment.objects.get_or_create(
        flat=flats["B-101"],
        charge_type=ChargeType.ADDITIONAL_CHARGE,
        source_request=mr2,
        defaults={
            "billing_month": "October 2026",
            "amount": Decimal("250.00"),
            "description": f"Maintenance Fee – (Request #{mr2.pk})",
            "status": PaymentStatus.UNPAID,
        },
    )
    print("   ✓ Billing records seeded")

    # ── VISITORS ─────────────────────────────────────────
    Visitor.objects.get_or_create(
        full_name="Delivery Person",
        contact_number="1234567890",
        target_flat=flats["A-101"],
        defaults={
            "purpose": "Delivery",
            "vehicle_type": VehicleType.BIKE,
            "vehicle_number": "KA01AB1234",
            "status": VisitorStatus.INSIDE,
        },
    )

    Visitor.objects.get_or_create(
        full_name="Plumber Joe",
        contact_number="0987654321",
        target_flat=flats["B-101"],
        defaults={
            "purpose": "Service/Maintenance",
            "status": VisitorStatus.CHECKED_OUT,
            "exit_time": timezone.now(),
        },
    )

    Visitor.objects.get_or_create(
        full_name="Anita Guest",
        contact_number="8765432109",
        target_flat=flats["A-102"],
        defaults={
            "purpose": "Guest",
            "vehicle_type": VehicleType.CAR,
            "vehicle_number": "MH02CD5678",
            "status": VisitorStatus.INSIDE,
        },
    )
    print("   ✓ Visitors seeded")

    print("\n✅ Seeding complete!")
    print("─" * 40)
    print("Login credentials:")
    print("  Admin    →  admin / admin123")
    print("  Guard    →  guard1 / guard123")
    print("  Resident →  resident1 / resident123  (Flat A-101) [Active]")
    print("  Resident →  resident2 / resident123  (Flat B-101) [Active]")
    print("  Resident →  resident3 / resident123  (Flat A-201) [Inactive]")
    print("  Resident →  resident4 / resident123  (Flat B-102) [Moved-out]")
    print("─" * 40)


if __name__ == "__main__":
    seed()
