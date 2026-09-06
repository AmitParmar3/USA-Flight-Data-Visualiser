"""
Flight Connection Analytics Package.

This package provides candidate flight connection generation, connection reliability analysis,
and multi-leg itinerary metrics.

DISTINCTION NOTICE:
-------------------
All connection metrics and candidate connections generated within this package are based on
schedule feasibility and operational timestamps from flight segment data. They DO NOT represent
observed passenger bookings or PNR / ticket data.
"""

from .generator import generate_candidate_connections, validate_candidate_connections
from .reliability import calculate_connection_reliability, calculate_missed_connection_risk
from .itinerary import calculate_itinerary_metrics

__all__ = [
    "generate_candidate_connections",
    "validate_candidate_connections",
    "calculate_connection_reliability",
    "calculate_missed_connection_risk",
    "calculate_itinerary_metrics",
]

