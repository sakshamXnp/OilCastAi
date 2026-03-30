import os
import sys
import logging
from datetime import timedelta

# Set up paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import SessionLocal
from database.models import Commodity, PriceData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard industry differentials against WTI (CL=F) or Brent (BZ=F)
# Format: { "Symbol": ("Base_Benchmark", Offset_USD) }
DIFFERENTIALS = {
    # Canadian
    "WCS": ("CL=F", -15.50),
    "CAN-CONDENSATE": ("CL=F", -2.00),
    "PREMIUM-SYNTH": ("CL=F", +1.20),
    "SWEET-SYNTH": ("CL=F", +0.50),
    "PEACE-SOUR": ("CL=F", -4.00),
    "CENTRAL-AB": ("CL=F", -3.50),
    "COLD-LAKE": ("CL=F", -16.00),
    "ALBIAN-HEAVY": ("CL=F", -14.50),
    
    # US Blends vs WTI
    "WTI-MIDLAND": ("CL=F", +1.10),
    "WTS": ("CL=F", -1.50),
    "EAGLE-FORD": ("CL=F", +1.80),
    "HLS": ("CL=F", +1.50),
    "LLS": ("CL=F", +2.10),
    "EUGENE-ISLAND": ("CL=F", -1.20),
    "LHS": ("CL=F", -2.50),
    "OK-SWEET": ("CL=F", -0.50),
    "OK-SOUR": ("CL=F", -2.00),
    "WY-SWEET": ("CL=F", -1.50),
    "WY-SOUR": ("CL=F", -4.50),
    "WY-ASPHALT": ("CL=F", -12.00),
    "DJ-BASIN": ("CL=F", -2.50),
    "NE-INTER": ("CL=F", -1.80),
    "MI-SWEET": ("CL=F", -1.00),
    "MI-SOUR": ("CL=F", -3.00),
    "KS-COMMON": ("CL=F", -1.50),
    "ANS": ("CL=F", +2.50),
    "AR-SWEET": ("CL=F", -0.80),
    "MARS": ("CL=F", -1.25),
    "POSEIDON": ("CL=F", -1.75),
    "SGC": ("CL=F", -2.20),
    "THUNDER-HORSE": ("CL=F", +0.80),
    
    # OPEC & International vs Brent
    "OPEC-BASKET": ("BZ=F", -1.50),
    "SAHARAN-BLEND": ("BZ=F", +0.50),
    "GIRASSOL": ("BZ=F", +0.80),
    "ORIENTE": ("BZ=F", -4.50),
    "IRAN-HEAVY": ("BZ=F", -2.50),
    "BASRAH-LIGHT": ("BZ=F", -1.00),
    "KUWAIT-EXPORT": ("BZ=F", -1.50),
    "ES-SIDER": ("BZ=F", +0.20),
    "BONNY-LIGHT": ("BZ=F", +1.20),
    "ARAB-LIGHT": ("BZ=F", -0.50),
    "UAE-MURBAN": ("BZ=F", +1.10),
    "MEREY": ("BZ=F", -14.00), # Heavy Venezuelan
    "DJENO": ("BZ=F", -1.80),
    "RABI-LIGHT": ("BZ=F", -0.50),
    "ZAFIRO": ("BZ=F", +0.40),
    
    # Russia
    "ESPO": ("BZ=F", -3.00),
    "URALS": ("BZ=F", -16.00), # Sanction discount
    "SOKOL": ("BZ=F", -4.00),
    
    # Others
    "MAYA": ("CL=F", -8.00),
    "ISTHMUS": ("CL=F", -2.50),
    "OLMECA": ("CL=F", +0.50),
    "UAE-DUBAI": ("BZ=F", -1.20),
    "UMM-SHAIF": ("BZ=F", +0.50),
    "QATAR-MARINE": ("BZ=F", -1.50),
    "QATAR-LAND": ("BZ=F", +0.20),
    "BASRAH-HEAVY": ("BZ=F", -4.50),
    "KIRKUK": ("BZ=F", -2.00),
    "ARAB-MEDIUM": ("BZ=F", -1.50),
    "ARAB-HEAVY": ("BZ=F", -3.50),
    "ARAB-XLIGHT": ("BZ=F", +1.50),
    "IRAN-LIGHT": ("BZ=F", -0.50),
    "FOROZAN": ("BZ=F", -1.50),
    "FORCADOS": ("BZ=F", +1.50),
    "QUA-IBOE": ("BZ=F", +1.80),
    "BRASS-RIVER": ("BZ=F", +1.40),
    "CABINDA": ("BZ=F", -0.50),
    "NEMBA": ("BZ=F", -1.00),
    "COSSACK": ("BZ=F", +1.50),
    "GIPPSLAND": ("BZ=F", +2.00),
    "AZERI-BTC": ("BZ=F", +2.50),
    "LULA": ("BZ=F", +1.20),
    "CPC-BLEND": ("BZ=F", -2.00),
    "TENGIZ": ("BZ=F", -1.50),
}


def simulate_regional_prices():
    """Generates synthetic price data for physical regional blends based on WTI/Brent."""
    logger.info("Starting synthetic regional pricing generation...")
    db = SessionLocal()
    
    # Get base benchmarks: WTI and BRENT
    wti_comm = db.query(Commodity).filter_by(symbol="CL=F").first()
    brent_comm = db.query(Commodity).filter_by(symbol="BZ=F").first()
    
    if not wti_comm or not brent_comm:
        logger.error("Base benchmarks (WTI/Brent) not found in database. Run ingestion first.")
        db.close()
        return

    # Load base prices into dictionaries keyed by timestamp
    wti_prices = {p.timestamp: p.price for p in db.query(PriceData).filter_by(commodity_id=wti_comm.id).all()}
    brent_prices = {p.timestamp: p.price for p in db.query(PriceData).filter_by(commodity_id=brent_comm.id).all()}
    
    bases = {
        "CL=F": wti_prices,
        "BZ=F": brent_prices
    }

    # Process all commodities
    all_comms = db.query(Commodity).all()
    count_generated = 0
    count_skipped = 0

    for comm in all_comms:
        if comm.symbol not in DIFFERENTIALS:
            continue
            
        base_sym, offset = DIFFERENTIALS[comm.symbol]
        base_history = bases.get(base_sym, {})
        
        if not base_history:
            continue

        logger.info(f"Generating synthetic data for {comm.name} ({comm.symbol}) using base {base_sym} {offset:+.2f}...")
        
        # Check what we already have for this commodity to avoid duplicate queries
        existing_price_dates = set(
            p.timestamp for p in db.query(PriceData.timestamp).filter_by(commodity_id=comm.id).all()
        )
        
        objects_to_add = []
        for timestamp, base_price in base_history.items():
            if timestamp in existing_price_dates:
                count_skipped += 1
                continue
                
            synthetic_price = max(1.0, base_price + offset) # Ensure prices don't go negative
            
            objects_to_add.append(PriceData(
                commodity_id=comm.id,
                price=synthetic_price,
                timestamp=timestamp,
                source="synthetic_differential"
            ))
            count_generated += 1
            
            if len(objects_to_add) >= 1000:
                db.bulk_save_objects(objects_to_add)
                objects_to_add = []
                
        if objects_to_add:
            db.bulk_save_objects(objects_to_add)
            
        db.commit()

    db.close()
    logger.info(f"Synthetic generation complete. Created {count_generated} records. Skipped {count_skipped} existing.")

if __name__ == "__main__":
    simulate_regional_prices()
