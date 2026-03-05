#!/usr/bin/env python3
import sys
import os
import json

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Offer
from scrapers.skills_extractor import is_alternance_offer
from scrapers.utils import is_school_offer

def cleanup_database():
    db = SessionLocal()
    try:
        offers = db.query(Offer).all()
        deleted_count = 0
        total = len(offers)
        
        print(f"Scanning {total} offers...")
        
        for offer in offers:
            # Check school status
            is_school = is_school_offer(offer.company, offer.description)
            # Check alternance status
            is_alternance = is_alternance_offer(offer.title, offer.description, offer.contract_type)
            
            should_delete = False
            reason = ""
            
            if is_school:
                should_delete = True
                reason = "Detected as school/training center"
            elif not is_alternance:
                should_delete = True
                reason = "Detected as non-alternance (CDI/CDD classique/Regulated prof)"
            
            if should_delete:
                print(f"DELETING [{offer.id}]: {offer.title} @ {offer.company}")
                print(f"  Reason: {reason}")
                db.delete(offer)
                deleted_count += 1
                
        db.commit()
        print(f"\nSUCCESS: Deleted {deleted_count} unwanted offers out of {total}.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_database()
