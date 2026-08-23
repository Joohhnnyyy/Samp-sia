"""
NeuroScrape / SaMp - Collective Memory Pruner (Section 3.3)
Removes degraded, low-confidence, or obsolete immune patterns on demand.
"""

import sys
import argparse
from pathlib import Path

# Add backend directory to sys.path
backend_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_root))

from app.healing.collective_memory import collective_memory


def main():
    parser = argparse.ArgumentParser(description="Prune degraded NeuroAnchor Collective Memory patterns")
    parser.add_argument("--min-conf", type=float, default=0.40, help="Minimum confidence threshold (default 0.40)")
    parser.add_argument("--days", type=int, default=30, help="Max age in days (default 30)")
    args = parser.parse_args()

    print(f"🧹 Scanning Collective Memory for patterns with confidence < {args.min_conf} or older than {args.days} days...")
    pruned = collective_memory.prune(min_confidence=args.min_conf, max_age_days=args.days)
    print(f"✅ Pruning complete. Removed {pruned} degraded patterns.")
    print(f"   Active immune patterns remaining: {len(collective_memory._memory_store)}")


if __name__ == "__main__":
    main()
