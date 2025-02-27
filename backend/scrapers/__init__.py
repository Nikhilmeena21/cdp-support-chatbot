from .segment_scraper import SegmentScraper
from .mparticle_scraper import MParticleScraper
from .lytics_scraper import LyticsScraper
from .zeotap_scraper import ZeotapScraper

def get_all_scrapers(output_dir):
    return [
        SegmentScraper(output_dir),
        MParticleScraper(output_dir),
        LyticsScraper(output_dir),
        ZeotapScraper(output_dir)
    ]