"""
Realistic dummy data generator: 10 PHCs across 3 Maharashtra districts,
30 medicines, real central government healthcare schemes plus 2 Maharashtra
state schemes, and several weeks of operational history (attendance, bed
occupancy, footfall, consumption) so that Module 2's forecasting has
something real to compute against.

This module only builds Python objects — `scripts/seed_db.py` is what
actually writes them to the database. Keeping generation separate from
writing makes this testable and reusable (e.g. from a pytest fixture).
"""

import random
from datetime import date, timedelta
from typing import List

from faker import Faker

from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.district import PHC, District
from app.models.inventory import Medicine, MedicineConsumptionLog, MedicineStock
from app.models.operations import AttendanceStatus, Bed, Doctor, DoctorAttendance, PatientFootfall
from app.models.scheme import RuleOperator, Scheme, SchemeDocument, SchemeLevel, SchemeRule

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

MAHARASHTRA_DISTRICTS = ["Nagpur", "Pune", "Nashik"]

PHC_NAMES_BY_DISTRICT = {
    "Nagpur": ["Kamptee PHC", "Hingna PHC", "Katol PHC", "Saoner PHC"],
    "Pune": ["Haveli PHC", "Maval PHC", "Khed PHC"],
    "Nashik": ["Igatpuri PHC", "Sinnar PHC", "Niphad PHC"],
}

MEDICINE_CATALOG = [
    ("Paracetamol 500mg", "Analgesic/Antipyretic", "strip"),
    ("Amoxicillin 500mg", "Antibiotic", "strip"),
    ("Oral Rehydration Salts (ORS)", "Electrolyte", "sachet"),
    ("Iron & Folic Acid Tablets", "Supplement", "strip"),
    ("Metformin 500mg", "Antidiabetic", "strip"),
    ("Amlodipine 5mg", "Antihypertensive", "strip"),
    ("Cetirizine 10mg", "Antihistamine", "strip"),
    ("Ibuprofen 400mg", "Analgesic", "strip"),
    ("Azithromycin 500mg", "Antibiotic", "strip"),
    ("Ciprofloxacin 500mg", "Antibiotic", "strip"),
    ("Vitamin D3 Sachet", "Supplement", "sachet"),
    ("Calcium Carbonate Tablets", "Supplement", "strip"),
    ("Albendazole 400mg", "Anthelmintic", "tablet"),
    ("Omeprazole 20mg", "Antacid", "strip"),
    ("Salbutamol Inhaler", "Bronchodilator", "inhaler"),
    ("Diazepam 5mg", "Anxiolytic", "strip"),
    ("Insulin Regular (Human)", "Antidiabetic", "vial"),
    ("Normal Saline IV Fluid", "IV Fluid", "bottle"),
    ("Ringer Lactate IV Fluid", "IV Fluid", "bottle"),
    ("Tetanus Toxoid Vaccine", "Vaccine", "vial"),
    ("BCG Vaccine", "Vaccine", "vial"),
    ("Measles-Rubella Vaccine", "Vaccine", "vial"),
    ("Oxytocin Injection", "Uterotonic", "vial"),
    ("Magnesium Sulphate Injection", "Anticonvulsant", "vial"),
    ("Chlorhexidine Antiseptic Solution", "Antiseptic", "bottle"),
    ("Povidone Iodine Solution", "Antiseptic", "bottle"),
    ("Disposable Syringes 5ml", "Consumable", "piece"),
    ("Surgical Gloves", "Consumable", "pair"),
    ("Cotton Gauze Roll", "Consumable", "roll"),
    ("Multivitamin Syrup (Pediatric)", "Supplement", "bottle"),
]

DOCTOR_SPECIALIZATIONS = [
    "General Medicine", "Gynaecology", "Pediatrics", "General Surgery", "Community Medicine",
]

FOOTFALL_DEPARTMENTS = ["General OPD", "Maternity", "Pediatrics", "Immunization", "Emergency"]

WARD_TYPES = ["General Ward", "Maternity Ward", "Isolation Ward"]


def _scheme_definitions() -> List[dict]:
    """Real, well-known Indian healthcare schemes, described in original
    wording (not copied from any government text), each with deterministic
    eligibility rules and document requirements the rule engine can evaluate."""
    return [
        {
            "name": "Ayushman Bharat – Pradhan Mantri Jan Arogya Yojana (AB-PMJAY)",
            "level": SchemeLevel.CENTRAL,
            "authority": "National Health Authority, Government of India",
            "description": (
                "A central government health assurance scheme that covers hospitalization "
                "expenses for economically vulnerable families, aiming to protect them from "
                "high out-of-pocket medical costs for secondary and tertiary care."
            ),
            "benefits_summary": (
                "Cashless hospitalization cover up to Rs. 5 lakh per family per year at empanelled "
                "hospitals, covering a wide range of medical and surgical procedures."
            ),
            "official_url": "https://pmjay.gov.in",
            "documents": [("Aadhaar Card", True), ("Ration Card", True), ("Family ID / SECC Verification", True)],
            "rules": [("annual_income", RuleOperator.LTE, "250000"), ("is_bpl_card_holder", RuleOperator.EQ, "true")],
        },
        {
            "name": "Janani Suraksha Yojana (JSY)",
            "level": SchemeLevel.CENTRAL,
            "authority": "Ministry of Health and Family Welfare, Government of India",
            "description": (
                "A safe motherhood intervention that promotes institutional delivery among "
                "pregnant women from low-income households to reduce maternal and infant mortality."
            ),
            "benefits_summary": (
                "Cash assistance for institutional delivery, along with support during antenatal "
                "and postnatal care visits at government facilities."
            ),
            "official_url": "https://nhm.gov.in",
            "documents": [("Aadhaar Card", True), ("Pregnancy Registration Card", True), ("BPL Certificate", False)],
            "rules": [("is_pregnant", RuleOperator.EQ, "true"), ("gender", RuleOperator.EQ, "female")],
        },
        {
            "name": "Pradhan Mantri Matru Vandana Yojana (PMMVY)",
            "level": SchemeLevel.CENTRAL,
            "authority": "Ministry of Women and Child Development, Government of India",
            "description": (
                "A maternity benefit program providing partial compensation for wage loss to "
                "pregnant and lactating women for their first living child."
            ),
            "benefits_summary": "Cash incentive paid in installments linked to pregnancy care milestones.",
            "official_url": "https://pmmvy.wcd.gov.in",
            "documents": [("Aadhaar Card", True), ("Bank Account Passbook", True), ("MCP Card", True)],
            "rules": [("is_pregnant", RuleOperator.EQ, "true")],
        },
        {
            "name": "Rashtriya Bal Swasthya Karyakram (RBSK)",
            "level": SchemeLevel.CENTRAL,
            "authority": "Ministry of Health and Family Welfare, Government of India",
            "description": (
                "A child health screening initiative that identifies developmental delays, "
                "birth defects, and deficiencies in children and links them to free treatment."
            ),
            "benefits_summary": "Free health screening and follow-up treatment for children up to 18 years.",
            "official_url": "https://rbsk.gov.in",
            "documents": [("Aadhaar Card or Birth Certificate", True)],
            "rules": [("age", RuleOperator.LTE, "18")],
        },
        {
            "name": "National Programme for Health Care of the Elderly (NPHCE)",
            "level": SchemeLevel.CENTRAL,
            "authority": "Ministry of Health and Family Welfare, Government of India",
            "description": (
                "Provides accessible, affordable geriatric healthcare services at PHC and "
                "district hospital level for senior citizens."
            ),
            "benefits_summary": "Free geriatric OPD consultation, screening, and basic medicines for elderly patients.",
            "official_url": "https://main.mohfw.gov.in",
            "documents": [("Aadhaar Card", True), ("Age Proof", True)],
            "rules": [("age", RuleOperator.GTE, "60")],
        },
        {
            "name": "Mahatma Jyotirao Phule Jan Arogya Yojana (MJPJAY)",
            "level": SchemeLevel.STATE,
            "authority": "Government of Maharashtra, State Health Assurance Society",
            "description": (
                "Maharashtra's state health assurance scheme offering cashless treatment for "
                "identified illnesses to economically weaker families across the state."
            ),
            "benefits_summary": (
                "Cashless medical and surgical treatment up to Rs. 1.5 lakh per family per year "
                "(higher for renal transplants) at network hospitals."
            ),
            "official_url": "https://www.jeevandayee.gov.in",
            "documents": [("Aadhaar Card", True), ("Orange/Yellow Ration Card", True), ("Domicile Certificate", True)],
            "rules": [("state", RuleOperator.EQ, "Maharashtra"), ("annual_income", RuleOperator.LTE, "100000")],
        },
        {
            "name": "Balasaheb Thackeray Apla Dawakhana Yojana",
            "level": SchemeLevel.STATE,
            "authority": "Government of Maharashtra, Public Health Department",
            "description": (
                "A neighbourhood clinic initiative set up by the Maharashtra government to give "
                "urban and semi-urban residents free consultations, diagnostics, and medicines "
                "close to where they live."
            ),
            "benefits_summary": "Free doctor consultation, free basic diagnostic tests, and free essential medicines.",
            "official_url": "https://arogya.maharashtra.gov.in",
            "documents": [("Any Government Photo ID", True)],
            "rules": [("state", RuleOperator.EQ, "Maharashtra")],
        },
    ]


def build_districts_and_phcs(session_add) -> List[PHC]:
    phcs: List[PHC] = []
    for district_name in MAHARASHTRA_DISTRICTS:
        district = District(name=district_name, state="Maharashtra")
        session_add(district)
        for phc_name in PHC_NAMES_BY_DISTRICT[district_name]:
            phc = PHC(
                district=district,
                name=phc_name,
                address=f"{phc_name}, {district_name} District, Maharashtra",
                latitude=round(random.uniform(18.5, 21.5), 6),
                longitude=round(random.uniform(73.5, 79.5), 6),
                contact_phone=f"+91{random.randint(7000000000, 9999999999)}",
            )
            session_add(phc)
            phcs.append(phc)
    return phcs


def build_medicines(session_add) -> List[Medicine]:
    medicines = []
    for name, category, unit in MEDICINE_CATALOG:
        medicine = Medicine(name=name, category=category, unit=unit, reorder_threshold=random.randint(15, 40))
        session_add(medicine)
        medicines.append(medicine)
    return medicines


def build_stock_and_consumption(session_add, phcs: List[PHC], medicines: List[Medicine]) -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    for phc in phcs:
        # Every PHC stocks every medicine, at a randomized level — some
        # deliberately low to make Module 2 forecasting/alerts meaningful.
        for medicine in medicines:
            is_deliberately_low = random.random() < 0.2
            quantity = (
                random.randint(0, medicine.reorder_threshold)
                if is_deliberately_low
                else random.randint(medicine.reorder_threshold, medicine.reorder_threshold * 6)
            )
            stock = MedicineStock(phc=phc, medicine=medicine, quantity=quantity)
            session_add(stock)

            # 14 days of consumption history with some day-to-day variance.
            base_daily_use = max(1, medicine.reorder_threshold // 15)
            for days_ago in range(14):
                if random.random() < 0.6:  # not every medicine is used every day
                    used = max(0, base_daily_use + random.randint(-1, 2))
                    if used > 0:
                        log = MedicineConsumptionLog(
                            phc=phc,
                            medicine=medicine,
                            quantity_used=used,
                            logged_at=now - timedelta(days=days_ago),
                        )
                        session_add(log)


def build_beds(session_add, phcs: List[PHC]) -> None:
    for phc in phcs:
        for ward_type in WARD_TYPES:
            total = random.randint(6, 20)
            occupied = random.randint(0, total)
            session_add(Bed(phc=phc, ward_type=ward_type, total_beds=total, occupied_beds=occupied))


def build_doctors_and_attendance(session_add, phcs: List[PHC]) -> None:
    today = date.today()
    for phc in phcs:
        num_doctors = random.randint(2, 5)
        doctors = []
        for _ in range(num_doctors):
            doctor = Doctor(phc=phc, name=fake.name(), specialization=random.choice(DOCTOR_SPECIALIZATIONS))
            session_add(doctor)
            doctors.append(doctor)

        for doctor in doctors:
            for days_ago in range(7):
                status = random.choices(
                    [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.ON_LEAVE],
                    weights=[0.8, 0.15, 0.05],
                )[0]
                attendance = DoctorAttendance(doctor=doctor, date=today - timedelta(days=days_ago), status=status)
                session_add(attendance)


def build_footfall(session_add, phcs: List[PHC]) -> None:
    today = date.today()
    for phc in phcs:
        for days_ago in range(7):
            for department in FOOTFALL_DEPARTMENTS:
                count = random.randint(2, 40)
                session_add(
                    PatientFootfall(phc=phc, date=today - timedelta(days=days_ago), department=department, count=count)
                )


def build_alerts(session_add, phcs: List[PHC]) -> None:
    sample_messages = [
        (AlertType.DOCTOR_ABSENT, AlertSeverity.MEDIUM, "Dr. on-duty roster shows an unfilled shift today."),
        (AlertType.BED_FULL, AlertSeverity.HIGH, "Maternity Ward is at full occupancy."),
    ]
    for phc in random.sample(phcs, k=min(4, len(phcs))):
        alert_type, severity, message = random.choice(sample_messages)
        session_add(Alert(phc=phc, type=alert_type, severity=severity, message=message))


def build_schemes(session_add) -> List[Scheme]:
    schemes = []
    for definition in _scheme_definitions():
        scheme = Scheme(
            name=definition["name"],
            level=definition["level"],
            authority=definition["authority"],
            description=definition["description"],
            benefits_summary=definition["benefits_summary"],
            official_url=definition["official_url"],
        )
        session_add(scheme)
        for doc_name, mandatory in definition["documents"]:
            session_add(SchemeDocument(scheme=scheme, document_name=doc_name, mandatory=mandatory))
        for field, operator, value in definition["rules"]:
            session_add(SchemeRule(scheme=scheme, field=field, operator=operator, value=value))
        schemes.append(scheme)
    return schemes
