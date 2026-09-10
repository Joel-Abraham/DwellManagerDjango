"""
DwellManager — Comprehensive Test Suite
Run: python manage.py test api -v 2
"""
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from .models import (
    Flat, Resident, MaintenanceRequest, Payment, Visitor,
    UserRole, MaintenanceStatus, PaymentStatus, VisitorStatus,
    ChargeType, ResidentStatus, MaintenanceCategory, VehicleType,
)


class BaseTestCase(TestCase):
    """Shared setup for all test classes."""

    def setUp(self):
        self.client = Client()

        # Flats
        self.flat_a = Flat.objects.create(
            flat_number="A-101", block="Block A", floor=1,
            flat_type="2BHK", owner_name="Owner A",
            base_maintenance_amount=Decimal("10000.00"),
        )
        self.flat_b = Flat.objects.create(
            flat_number="B-101", block="Block B", floor=1,
            flat_type="3BHK", owner_name="Owner B",
            base_maintenance_amount=Decimal("15000.00"),
        )

        # Admin
        self.admin = Resident.objects.create_superuser(
            username="admin", password="admin123",
            full_name="Test Admin", role=UserRole.ADMIN,
        )

        # Guard
        self.guard = Resident.objects.create_user(
            username="guard1", password="guard123",
            full_name="Test Guard", role=UserRole.GUARD,
        )

        # Resident 1 -> Flat A
        self.resident1 = Resident.objects.create_user(
            username="resident1", password="resident123",
            full_name="Resident One", role=UserRole.RESIDENT,
            flat=self.flat_a,
        )

        # Resident 2 -> Flat B
        self.resident2 = Resident.objects.create_user(
            username="resident2", password="resident123",
            full_name="Resident Two", role=UserRole.RESIDENT,
            flat=self.flat_b,
        )


# ============================================================
# FLAT TESTS
# ============================================================

class FlatTests(BaseTestCase):

    def test_admin_can_create_flat(self):
        self.client.login(username="admin", password="admin123")
        resp = self.client.post(reverse("admin_flat_create"), {
            "flat_number": "C-101",
            "block": "Block C",
            "floor": 1,
            "flat_type": "1BHK",
            "owner_name": "New Owner",
            "base_maintenance_amount": "5000.00",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Flat.objects.filter(flat_number="C-101").exists())

    def test_admin_can_edit_flat(self):
        self.client.login(username="admin", password="admin123")
        resp = self.client.post(
            reverse("admin_flat_edit", args=[self.flat_a.pk]),
            {
                "flat_number": "A-101",
                "block": "Block A",
                "floor": 1,
                "flat_type": "3BHK",
                "owner_name": "Updated Owner",
                "base_maintenance_amount": "12000.00",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.flat_a.refresh_from_db()
        self.assertEqual(self.flat_a.owner_name, "Updated Owner")

    def test_admin_can_deactivate_flat(self):
        self.client.login(username="admin", password="admin123")
        resp = self.client.post(
            reverse("admin_flat_deactivate", args=[self.flat_a.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.flat_a.refresh_from_db()
        self.assertFalse(self.flat_a.is_active)

    def test_deactivated_flat_remains_in_database(self):
        self.client.login(username="admin", password="admin123")
        self.client.post(reverse("admin_flat_deactivate", args=[self.flat_a.pk]))
        self.assertTrue(Flat.objects.filter(pk=self.flat_a.pk).exists())

    def test_resident_cannot_access_flat_management(self):
        self.client.login(username="resident1", password="resident123")
        resp = self.client.get(reverse("admin_flat_list"))
        self.assertEqual(resp.status_code, 403)


# ============================================================
# RESIDENT MANAGEMENT TESTS
# ============================================================

class ResidentManagementTests(BaseTestCase):

    def test_admin_can_create_resident(self):
        self.client.login(username="admin", password="admin123")
        resp = self.client.post(reverse("admin_resident_create"), {
            "username": "newresident",
            "full_name": "New Resident",
            "flat": self.flat_a.pk,
            "password": "testpass123",
            "contact_number": "1234567890",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Resident.objects.filter(username="newresident").exists())

    def test_admin_can_edit_resident(self):
        self.client.login(username="admin", password="admin123")
        resp = self.client.post(
            reverse("admin_resident_edit", args=[self.resident1.pk]),
            {
                "username": "resident1",
                "full_name": "Updated Name",
                "flat": self.flat_a.pk,
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.resident1.refresh_from_db()
        self.assertEqual(self.resident1.full_name, "Updated Name")

    def test_admin_can_deactivate_resident(self):
        self.client.login(username="admin", password="admin123")
        resp = self.client.post(
            reverse("admin_resident_deactivate", args=[self.resident1.pk])
        )
        self.assertEqual(resp.status_code, 302)
        self.resident1.refresh_from_db()
        self.assertEqual(self.resident1.status, ResidentStatus.INACTIVE)


# ============================================================
# MAINTENANCE REQUEST TESTS
# ============================================================

class MaintenanceTests(BaseTestCase):

    def test_resident_can_create_maintenance_request(self):
        self.client.login(username="resident1", password="resident123")
        resp = self.client.post(reverse("resident_request_maintenance"), {
            "category": MaintenanceCategory.PLUMBING,
            "description": "Tap is leaking.",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            MaintenanceRequest.objects.filter(flat=self.flat_a).exists()
        )

    def test_resident_request_uses_own_flat(self):
        self.client.login(username="resident1", password="resident123")
        self.client.post(reverse("resident_request_maintenance"), {
            "category": MaintenanceCategory.ELECTRICAL,
            "description": "Socket issue",
        })
        req = MaintenanceRequest.objects.latest("created_at")
        self.assertEqual(req.flat, self.flat_a)

    def test_resident_cannot_assign_another_flat(self):
        """Even if somehow a flat field was submitted, it must be ignored."""
        self.client.login(username="resident1", password="resident123")
        self.client.post(reverse("resident_request_maintenance"), {
            "category": MaintenanceCategory.PLUMBING,
            "description": "Test",
            "flat": self.flat_b.pk,  # Attempt to use flat B
        })
        req = MaintenanceRequest.objects.latest("created_at")
        # Must still be assigned to resident1's flat (A), not flat B
        self.assertEqual(req.flat, self.flat_a)

    def test_admin_can_assign_request(self):
        self.client.login(username="admin", password="admin123")
        mreq = MaintenanceRequest.objects.create(
            flat=self.flat_a,
            category=MaintenanceCategory.PLUMBING,
            description="Test",
            status=MaintenanceStatus.PENDING,
        )
        resp = self.client.post(
            reverse("admin_maintenance_assign", args=[mreq.pk]),
            {
                "assigned_to": "Plumber Bob",
                "scheduled_date": "2026-10-01",
                "fee_amount": "500.00",
            },
        )
        self.assertEqual(resp.status_code, 302)
        mreq.refresh_from_db()
        self.assertEqual(mreq.status, MaintenanceStatus.ASSIGNED)
        self.assertEqual(mreq.assigned_to, "Plumber Bob")

    def test_assignment_generates_additional_charge(self):
        self.client.login(username="admin", password="admin123")
        mreq = MaintenanceRequest.objects.create(
            flat=self.flat_a,
            category=MaintenanceCategory.ELECTRICAL,
            description="Sparks",
            status=MaintenanceStatus.PENDING,
        )
        self.client.post(
            reverse("admin_maintenance_assign", args=[mreq.pk]),
            {
                "assigned_to": "Electrician",
                "scheduled_date": "2026-10-01",
                "fee_amount": "300.00",
            },
        )
        charge = Payment.objects.filter(
            source_request=mreq,
            charge_type=ChargeType.ADDITIONAL_CHARGE,
        )
        self.assertTrue(charge.exists())
        self.assertEqual(charge.first().amount, Decimal("300.00"))

    def test_assignment_and_charge_are_atomic(self):
        """If charge creation somehow fails, assignment should roll back."""
        self.client.login(username="admin", password="admin123")
        mreq = MaintenanceRequest.objects.create(
            flat=self.flat_a,
            category=MaintenanceCategory.PLUMBING,
            description="Test atomicity",
            status=MaintenanceStatus.PENDING,
        )
        # Assign with zero fee — should succeed without creating charge
        self.client.post(
            reverse("admin_maintenance_assign", args=[mreq.pk]),
            {
                "assigned_to": "Tech",
                "scheduled_date": "2026-10-01",
                "fee_amount": "0.00",
            },
        )
        mreq.refresh_from_db()
        self.assertEqual(mreq.status, MaintenanceStatus.ASSIGNED)
        self.assertFalse(
            Payment.objects.filter(source_request=mreq).exists()
        )

    def test_failed_charge_creation_rolls_assignment_back(self):
        """Cannot assign a non-Pending request."""
        self.client.login(username="admin", password="admin123")
        mreq = MaintenanceRequest.objects.create(
            flat=self.flat_a,
            category=MaintenanceCategory.PLUMBING,
            description="Already assigned",
            status=MaintenanceStatus.ASSIGNED,
        )
        resp = self.client.post(
            reverse("admin_maintenance_assign", args=[mreq.pk]),
            {
                "assigned_to": "Tech",
                "scheduled_date": "2026-10-01",
                "fee_amount": "100.00",
            },
        )
        self.assertEqual(resp.status_code, 302)  # Redirect with error
        self.assertFalse(
            Payment.objects.filter(source_request=mreq).exists()
        )


# ============================================================
# BILLING / PAYMENT TESTS
# ============================================================

class BillingTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        # Create charges for both flats
        self.charge_a = Payment.objects.create(
            flat=self.flat_a,
            charge_type=ChargeType.BASE_MAINTENANCE,
            billing_month="Sep 2026",
            amount=Decimal("10000.00"),
            description="Monthly Maintenance",
            status=PaymentStatus.UNPAID,
        )
        self.charge_b = Payment.objects.create(
            flat=self.flat_b,
            charge_type=ChargeType.BASE_MAINTENANCE,
            billing_month="Sep 2026",
            amount=Decimal("15000.00"),
            description="Monthly Maintenance",
            status=PaymentStatus.UNPAID,
        )

    def test_resident_sees_only_own_flat_billing(self):
        self.client.login(username="resident1", password="resident123")
        resp = self.client.get(reverse("resident_billing"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "10000.00")
        self.assertNotContains(resp, "15000.00")

    def test_resident_cannot_access_another_flat_charge(self):
        """IDOR test: resident1 tries to pay charge belonging to flat B."""
        self.client.login(username="resident1", password="resident123")
        resp = self.client.get(
            reverse("resident_pay_charge", args=[self.charge_b.pk])
        )
        self.assertEqual(resp.status_code, 404)

    def test_resident_payment_changes_status(self):
        self.client.login(username="resident1", password="resident123")
        resp = self.client.post(
            reverse("resident_pay_charge", args=[self.charge_a.pk]),
            {"payment_method": "UPI"},
        )
        self.assertEqual(resp.status_code, 200)  # Receipt page
        self.charge_a.refresh_from_db()
        self.assertEqual(self.charge_a.status, PaymentStatus.PAID)

    def test_paid_at_is_populated(self):
        self.client.login(username="resident1", password="resident123")
        self.client.post(
            reverse("resident_pay_charge", args=[self.charge_a.pk]),
            {"payment_method": "UPI"},
        )
        self.charge_a.refresh_from_db()
        self.assertIsNotNone(self.charge_a.paid_at)

    def test_double_payment_rejected(self):
        self.client.login(username="resident1", password="resident123")
        # First payment
        self.client.post(
            reverse("resident_pay_charge", args=[self.charge_a.pk]),
            {"payment_method": "UPI"},
        )
        # Second attempt
        resp = self.client.post(
            reverse("resident_pay_charge", args=[self.charge_a.pk]),
            {"payment_method": "UPI"},
        )
        self.assertEqual(resp.status_code, 302)  # Redirect with error


# ============================================================
# VISITOR TESTS
# ============================================================

class VisitorTests(BaseTestCase):

    def test_guard_can_check_in_visitor(self):
        self.client.login(username="guard1", password="guard123")
        resp = self.client.post(reverse("guard_dashboard"), {
            "full_name": "Test Visitor",
            "contact_number": "1234567890",
            "target_flat": self.flat_a.pk,
            "purpose": "Delivery",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(
            Visitor.objects.filter(full_name="Test Visitor").exists()
        )

    def test_guard_sees_inside_visitors(self):
        Visitor.objects.create(
            full_name="Inside Visitor",
            contact_number="1111111111",
            target_flat=self.flat_a,
            purpose="Guest",
            status=VisitorStatus.INSIDE,
        )
        self.client.login(username="guard1", password="guard123")
        resp = self.client.get(reverse("guard_dashboard"))
        self.assertContains(resp, "Inside Visitor")

    def test_checkout_changes_status(self):
        visitor = Visitor.objects.create(
            full_name="Checkout Test",
            contact_number="2222222222",
            target_flat=self.flat_a,
            purpose="Delivery",
            status=VisitorStatus.INSIDE,
        )
        self.client.login(username="guard1", password="guard123")
        resp = self.client.post(
            reverse("guard_visitor_checkout", args=[visitor.pk])
        )
        self.assertEqual(resp.status_code, 302)
        visitor.refresh_from_db()
        self.assertEqual(visitor.status, VisitorStatus.CHECKED_OUT)

    def test_exit_time_saved_on_checkout(self):
        visitor = Visitor.objects.create(
            full_name="Time Test",
            contact_number="3333333333",
            target_flat=self.flat_a,
            purpose="Guest",
            status=VisitorStatus.INSIDE,
        )
        self.client.login(username="guard1", password="guard123")
        self.client.post(
            reverse("guard_visitor_checkout", args=[visitor.pk])
        )
        visitor.refresh_from_db()
        self.assertIsNotNone(visitor.exit_time)

    def test_already_checked_out_visitor_returns_error(self):
        visitor = Visitor.objects.create(
            full_name="Already Out",
            contact_number="4444444444",
            target_flat=self.flat_a,
            purpose="Delivery",
            status=VisitorStatus.CHECKED_OUT,
            exit_time=timezone.now(),
        )
        self.client.login(username="guard1", password="guard123")
        resp = self.client.post(
            reverse("guard_visitor_checkout", args=[visitor.pk]),
            follow=True,
        )
        self.assertContains(resp, "Visitor already checked out")

    def test_visitor_history_is_read_only(self):
        """Guard log page should be GET only — no modification."""
        self.client.login(username="guard1", password="guard123")
        resp = self.client.get(reverse("guard_visitor_log"))
        self.assertEqual(resp.status_code, 200)


# ============================================================
# SECURITY / IDOR TESTS
# ============================================================

class SecurityTests(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.mreq_a = MaintenanceRequest.objects.create(
            flat=self.flat_a,
            category=MaintenanceCategory.PLUMBING,
            description="Flat A request",
        )
        self.mreq_b = MaintenanceRequest.objects.create(
            flat=self.flat_b,
            category=MaintenanceCategory.ELECTRICAL,
            description="Flat B request",
        )
        self.charge_a = Payment.objects.create(
            flat=self.flat_a,
            charge_type=ChargeType.ADDITIONAL_CHARGE,
            billing_month="Sep 2026",
            amount=Decimal("500.00"),
            status=PaymentStatus.UNPAID,
        )
        self.charge_b = Payment.objects.create(
            flat=self.flat_b,
            charge_type=ChargeType.ADDITIONAL_CHARGE,
            billing_month="Sep 2026",
            amount=Decimal("600.00"),
            status=PaymentStatus.UNPAID,
        )

    def test_resident1_cannot_access_resident2_maintenance_request(self):
        """resident1 (A-101) should not see B-101 requests."""
        self.client.login(username="resident1", password="resident123")
        resp = self.client.get(reverse("resident_my_requests"))
        self.assertNotContains(resp, "Flat B request")
        self.assertContains(resp, "Flat A request")

    def test_resident1_cannot_access_resident2_charge(self):
        self.client.login(username="resident1", password="resident123")
        resp = self.client.get(
            reverse("resident_pay_charge", args=[self.charge_b.pk])
        )
        self.assertEqual(resp.status_code, 404)

    def test_resident1_cannot_pay_resident2_charge(self):
        self.client.login(username="resident1", password="resident123")
        resp = self.client.post(
            reverse("resident_pay_charge", args=[self.charge_b.pk]),
            {"payment_method": "UPI"},
        )
        self.assertEqual(resp.status_code, 404)
        self.charge_b.refresh_from_db()
        self.assertEqual(self.charge_b.status, PaymentStatus.UNPAID)

    def test_resident1_cannot_access_resident2_billing(self):
        self.client.login(username="resident1", password="resident123")
        resp = self.client.get(reverse("resident_billing"))
        self.assertNotContains(resp, "600.00")

    def test_guard_cannot_access_admin_pages(self):
        self.client.login(username="guard1", password="guard123")
        resp = self.client.get(reverse("admin_flat_list"))
        self.assertEqual(resp.status_code, 403)

    def test_resident_cannot_access_guard_pages(self):
        self.client.login(username="resident1", password="resident123")
        resp = self.client.get(reverse("guard_dashboard"))
        self.assertEqual(resp.status_code, 403)

    def test_unauthenticated_redirects_to_login(self):
        resp = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/", resp.url)


# ============================================================
# AUTH TESTS
# ============================================================

class AuthTests(BaseTestCase):

    def test_login_redirects_admin_to_admin_dashboard(self):
        resp = self.client.post(reverse("login"), {
            "username": "admin",
            "password": "admin123",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, reverse("admin_dashboard"))

    def test_login_redirects_guard_to_guard_dashboard(self):
        resp = self.client.post(reverse("login"), {
            "username": "guard1",
            "password": "guard123",
        })
        self.assertRedirects(resp, reverse("guard_dashboard"))

    def test_login_redirects_resident_to_resident_dashboard(self):
        resp = self.client.post(reverse("login"), {
            "username": "resident1",
            "password": "resident123",
        })
        self.assertRedirects(resp, reverse("resident_dashboard"))

    def test_invalid_login_shows_error(self):
        resp = self.client.post(reverse("login"), {
            "username": "admin",
            "password": "wrongpass",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Invalid username or password")

    def test_logout_redirects_to_login(self):
        self.client.login(username="admin", password="admin123")
        resp = self.client.get(reverse("logout"))
        self.assertRedirects(resp, reverse("login"))
