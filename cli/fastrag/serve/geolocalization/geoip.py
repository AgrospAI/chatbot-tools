import logging
from pathlib import Path
from typing import Optional

import geoip2.database
from geoip2.errors import AddressNotFoundError

logger = logging.getLogger(__name__)

# Path to GeoLite2-Country database file
# You can download it from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data
GEOIP_DB_PATH = Path(__file__).parent / "GeoLite2-Country.mmdb"


def get_country_from_ip(ip_address: str) -> Optional[str]:
    """
    Get the country code from an IP address using GeoIP2.

    Args:
        ip_address: The IP address to lookup

    Returns:
        ISO country code (e.g., 'US', 'ES', 'GB') or None if not found
    """
    # Skip private/local IP addresses
    if not ip_address or ip_address in ["127.0.0.1", "localhost", "::1"]:
        return None

    # Check if database file exists
    if not GEOIP_DB_PATH.exists():
        logger.warning(
            f"GeoIP2 database not found at {GEOIP_DB_PATH}. "
            "Download it from https://dev.maxmind.com/geoip/geolite2-free-geolocation-data"
        )
        return None

    try:
        with geoip2.database.Reader(str(GEOIP_DB_PATH)) as reader:
            response = reader.country(ip_address)
            return response.country.iso_code
    except AddressNotFoundError:
        logger.debug(f"IP address {ip_address} not found in GeoIP2 database")
        return None
    except Exception as e:
        logger.error(f"Error looking up IP {ip_address}: {e}")
        return None
