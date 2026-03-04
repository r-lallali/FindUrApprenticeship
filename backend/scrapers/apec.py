import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from curl_cffi.requests import AsyncSession
from scrapers.base_scraper import BaseScraper
from scrapers.utils import is_school_offer, clean_text, enrich_location, normalize_salary

class ApecScraper(BaseScraper):
    """Scraper for Apec.fr using the CMS webservices API."""

    BASE_URL = "https://www.apec.fr"
    # New working API endpoint discovered by subagent
    SEARCH_API_URL = "https://www.apec.fr/cms/webservices/rechercheOffre"

    def __init__(self):
        super().__init__("apec")

    async def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        search_terms = kwargs.get("search_terms", ["alternance", "apprentissage"])
        all_offers = []
        seen_ids = set()

        async with AsyncSession(impersonate="chrome110") as session:
            for term in search_terms:
                self.logger.info(f"Apec: Searching for '{term}'")
                # Using the exact payload structure from the subagent
                payload = {
                    "lieux": [],
                    "fonctions": [],
                    "statutPoste": [],
                    "typesContrat": [],
                    "typesConvention": ["143684", "143685", "143686", "143687", "143706"], # All alternance types
                    "pagination": {"range": 50, "startIndex": 0},
                    "motsCles": term,
                    "typeClient": "CADRE",
                    "sorts": [{"type": "SCORE", "direction": "DESCENDING"}],
                    "activeFiltre": True
                }
                
                try:
                    response = await session.post(
                        self.SEARCH_API_URL, 
                        json=payload,
                        headers={
                            "Accept": "application/json, text/plain, */*",
                            "Origin": "https://www.apec.fr",
                            "Referer": f"https://www.apec.fr/candidat/recherche-emploi.html/emploi?motsCles={term}"
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Apec response structure for this API is a bit different
                        results = data.get("resultats", [])
                        self.logger.info(f"Apec: Found {len(results)} results for '{term}'")
                        if results:
                            self.logger.info(f"First result keys: {results[0].keys()}")
                        for item in results:
                            oid = item.get("numeroOffre")
                            if oid and oid not in seen_ids:
                                seen_ids.add(oid)
                                all_offers.append(item)
                    else:
                        self.logger.warning(f"Apec search failed with status {response.status_code} for '{term}'")
                except Exception as e:
                    self.logger.error(f"Error in Apec scrape for '{term}': {e}")
                
                await asyncio.sleep(1)

        return all_offers

    def parse_offer(self, raw_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            oid = raw_data.get("numeroOffre")
            if not oid:
                return None
                
            title = raw_data.get("intitule", "")
            company = raw_data.get("nomCommercial") or raw_data.get("nomEntreprise") or "Entreprise confidentielle"
            location = raw_data.get("lieuTexte") or raw_data.get("lieu", "")
            description = raw_data.get("texteOffre") or raw_data.get("description", "")
            
            # Publication date
            pub_date = None
            ts = raw_data.get("datePublication") # Timestamp in ms
            if ts:
                try:
                    pub_date = datetime.fromtimestamp(int(ts) / 1000.0)
                except (ValueError, TypeError):
                    pass
            
            # URL
            url = f"https://www.apec.fr/candidat/recherche-emploi.html/emploi/detail-offre/{oid}"
            
            is_school = is_school_offer(company, description)
            cloc = clean_text(location)
            enriched_loc, dept = enrich_location(cloc)
            
            return {
                "title": clean_text(title),
                "company": clean_text(company),
                "location": enriched_loc or cloc,
                "department": dept,
                "contract_type": "Alternance",
                "salary": raw_data.get("salaireTexte"),
                "description": clean_text(description),
                "profile": None,
                "category": None,
                "publication_date": pub_date or datetime.now(),
                "source": "apec",
                "url": url,
                "source_id": f"apec_{oid}",
                "is_school": is_school,
            }
        except Exception as e:
            self.logger.warning(f"Error parsing Apec offer: {e}")
            return None


