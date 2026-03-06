
import os
import sys
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the backend directory is in the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from database import DATABASE_URL
from models import Offer
from scrapers import LaBonneAlternanceScraper

async def repair_lba_descriptions():
    print(f"Connecting to database to find LBA offers with missing descriptions...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Find LBA offers with missing/generic descriptions
        offers = session.query(Offer).filter(
            Offer.source == 'labonnealternance'
        ).filter(
            (Offer.description == None) | 
            (Offer.description == '') | 
            (Offer.description.like('%non disponible%'))
        ).all()
        
        if not offers:
            print("No LBA offers to repair.")
            return

        print(f"Found {len(offers)} LBA offers to repair.")
        
        # We'll run the scraper for all common ROMEs used in the project
        # This is more efficient than searching one by one
        scraper = LaBonneAlternanceScraper()
        
        # Collect IDs we are looking for
        target_ids = {o.source_id: o for o in offers}
        
        # Common ROMEs from the scraper + others found in logs
        romes = []
        for codes in scraper.ROME_CODES.values():
            romes.extend(codes)
        
        # Add extra ROMEs if necessary
        for r in ["N1301", "H2502", "H1205", "M1601", "M1602"]:
            if r not in romes:
                romes.append(r)
        
        print("Running searches in LBA API to find matching descriptions...")
        all_found = 0
        
        # We can do this in chunks or just run the scraper's search
        for i, rome in enumerate(romes):
            print(f"[{i+1}/{len(romes)}] Searching ROME: {rome}...")
            try:
                # Scrape raw results
                raw_results = await scraper.scrape(rome_codes=[rome], radius=100)
                
                for raw in raw_results:
                    # Get internal type and ID to reconstruct source_id
                    idea_type = raw.get("ideaType", "")
                    # matcha uses 'id', others use 'job.id'
                    oid = raw.get("id") or raw.get("job", {}).get("id")
                    
                    if not oid: continue
                    
                    sid = f"lba_{idea_type}_{oid}"
                    
                    if sid in target_ids:
                        offer = target_ids[sid]
                        # Parse it to get the description (including fallback)
                        parsed = scraper.parse_offer(raw)
                        if parsed and parsed.get("description"):
                            offer.description = parsed["description"]
                            print(f"  FIXED: {offer.title[:40]}... ({sid})")
                            all_found += 1
                            # Don't delete from targets yet, might be duplicates
                
                # Commit every rome to be safe
                session.commit()
            except Exception as e:
                print(f"  Error searching {rome}: {e}")

        print(f"Finished repairing LBA descriptions. Total fixed: {all_found}/{len(offers)}")
    finally:
        session.close()

if __name__ == "__main__":
    asyncio.run(repair_lba_descriptions())
