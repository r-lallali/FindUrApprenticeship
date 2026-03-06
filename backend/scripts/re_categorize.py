
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the backend directory is in the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from database import DATABASE_URL
from models import Offer
from scrapers.skills_extractor import categorize_offer

def re_categorize_all():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        offers = session.query(Offer).all()
        total = len(offers)
        print(f"Found {total} offers. Starting re-categorization...")

        changed_count = 0
        for i, offer in enumerate(offers):
            old_cat = offer.category
            new_cat = categorize_offer(offer.title, offer.description)
            
            if old_cat != new_cat:
                offer.category = new_cat
                changed_count += 1
            
            if (i + 1) % 500 == 0:
                print(f"Processed {i + 1}/{total} offers...")
                session.commit()

        session.commit()
        print(f"Finished! Updated {changed_count} offers out of {total}.")
    except Exception as e:
        session.rollback()
        print(f"Error during migration: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    re_categorize_all()
