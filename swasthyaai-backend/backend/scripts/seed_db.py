"""
Seeds the database with the dummy dataset described in docs/ARCHITECTURE.md
section 10: 10 PHCs across 3 Maharashtra districts, 30 medicines, and real
central + Maharashtra state healthcare schemes, plus several weeks of
operational history.

Usage:
    python -m scripts.seed_db
    python -m scripts.seed_db --reset   # drops and recreates all seeded rows

This script is idempotent when run without --reset: it checks for existing
districts before inserting, so re-running it after a partial failure won't
duplicate the whole dataset.
"""

import argparse
import sys

from sqlalchemy import text

from app.core.logging import configure_logging, get_logger
from app.db.session import SessionLocal
from scripts.generate_dummy_data import (
    build_alerts,
    build_beds,
    build_districts_and_phcs,
    build_doctors_and_attendance,
    build_footfall,
    build_medicines,
    build_schemes,
    build_stock_and_consumption,
)

configure_logging()
logger = get_logger(__name__)

_TABLES_TO_TRUNCATE = [
    "eligibility_check_log",
    "ai_interaction_log",
    "alerts",
    "patient_footfall",
    "doctor_attendance",
    "doctors",
    "beds",
    "medicine_consumption_log",
    "medicine_stock",
    "scheme_rules",
    "scheme_documents",
    "schemes",
    "medicines",
    "phcs",
    "districts",
]


def reset(db) -> None:
    logger.info("resetting_seed_tables")
    for table in _TABLES_TO_TRUNCATE:
        db.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
    db.commit()


def already_seeded(db) -> bool:
    result = db.execute(text("SELECT COUNT(*) FROM districts")).scalar_one()
    return result > 0


def seed(db) -> None:
    added_objects = []

    def add(obj):
        db.add(obj)
        added_objects.append(obj)

    logger.info("seeding_districts_and_phcs")
    phcs = build_districts_and_phcs(add)
    db.flush()

    logger.info("seeding_medicines")
    medicines = build_medicines(add)
    db.flush()

    logger.info("seeding_stock_and_consumption")
    build_stock_and_consumption(add, phcs, medicines)

    logger.info("seeding_beds")
    build_beds(add, phcs)

    logger.info("seeding_doctors_and_attendance")
    build_doctors_and_attendance(add, phcs)

    logger.info("seeding_footfall")
    build_footfall(add, phcs)

    logger.info("seeding_alerts")
    build_alerts(add, phcs)

    logger.info("seeding_schemes")
    build_schemes(add)

    db.commit()
    logger.info("seed_complete", objects_created=len(added_objects))


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the SwasthyaAI database with dummy data.")
    parser.add_argument("--reset", action="store_true", help="Truncate seeded tables before inserting.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        if args.reset:
            reset(db)
        elif already_seeded(db):
            logger.info("database_already_seeded_skipping")
            print("Database already contains seed data. Use --reset to reseed.")
            return

        seed(db)
        print("Seed data inserted successfully.")
    except Exception:
        db.rollback()
        logger.error("seed_failed", exc_info=True)
        print("Seeding failed — see logs above.", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
