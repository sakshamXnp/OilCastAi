import logging
from database.database import SessionLocal, Base, engine
from database.models import Commodity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_commodities():
    logger.info("Seeding commodity metadata...")
    db = SessionLocal()
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    commodities = [
        # ============================================================
        # FUTURES & INDEXES
        # ============================================================
        {"name": "WTI Crude Oil", "symbol": "CL=F", "category": "FUTURES", "region": "USA"},
        {"name": "Brent Crude Oil", "symbol": "BZ=F", "category": "FUTURES", "region": "Global"},
        {"name": "Murban Crude Oil", "symbol": "MURBN.ME", "category": "FUTURES", "region": "Middle East"},
        {"name": "Natural Gas", "symbol": "NG=F", "category": "FUTURES", "region": "USA"},
        {"name": "RBOB Gasoline", "symbol": "RB=F", "category": "FUTURES", "region": "USA"},
        {"name": "Heating Oil", "symbol": "HO=F", "category": "FUTURES", "region": "USA"},
        {"name": "Mars US (GC)", "symbol": "GC=F", "category": "FUTURES", "region": "USA"},
        {"name": "OPEC Basket", "symbol": "OP=F", "category": "FUTURES", "region": "Global"},
        {"name": "Canadian Crude Index", "symbol": "CCI=F", "category": "FUTURES", "region": "Canada"},
        {"name": "Dubai Crude (DME Oman)", "symbol": "DCB=F", "category": "FUTURES", "region": "Middle East"},

        # ============================================================
        # OPEC MEMBERS
        # ============================================================
        {"name": "OPEC Basket (Daily)", "symbol": "OPEC-BASKET", "category": "OPEC", "region": "Global"},
        {"name": "Algeria Saharan Blend", "symbol": "SAHARAN-BLEND", "category": "OPEC", "region": "Algeria"},
        {"name": "Angola Girassol", "symbol": "GIRASSOL", "category": "OPEC", "region": "Angola"},
        {"name": "Ecuador Oriente", "symbol": "ORIENTE", "category": "OPEC", "region": "Ecuador"},
        {"name": "Iran Heavy", "symbol": "IRAN-HEAVY", "category": "OPEC", "region": "Iran"},
        {"name": "Iraq Basrah Light", "symbol": "BASRAH-LIGHT", "category": "OPEC", "region": "Iraq"},
        {"name": "Kuwait Export", "symbol": "KUWAIT-EXPORT", "category": "OPEC", "region": "Kuwait"},
        {"name": "Libya Es Sider", "symbol": "ES-SIDER", "category": "OPEC", "region": "Libya"},
        {"name": "Nigeria Bonny Light", "symbol": "BONNY-LIGHT", "category": "OPEC", "region": "Nigeria"},
        {"name": "Saudi Arab Light", "symbol": "ARAB-LIGHT", "category": "OPEC", "region": "Saudi Arabia"},
        {"name": "UAE Murban", "symbol": "UAE-MURBAN", "category": "OPEC", "region": "UAE"},
        {"name": "Venezuela Merey", "symbol": "MEREY", "category": "OPEC", "region": "Venezuela"},
        {"name": "Congo Djeno", "symbol": "DJENO", "category": "OPEC", "region": "Congo"},
        {"name": "Gabon Rabi Light", "symbol": "RABI-LIGHT", "category": "OPEC", "region": "Gabon"},
        {"name": "Equatorial Guinea Zafiro", "symbol": "ZAFIRO", "category": "OPEC", "region": "Equatorial Guinea"},

        # ============================================================
        # INTERNATIONAL PRICES
        # ============================================================
        # Russia
        {"name": "Russia ESPO Blend", "symbol": "ESPO", "category": "INTERNATIONAL", "region": "Russia"},
        {"name": "Russia Urals", "symbol": "URALS", "category": "INTERNATIONAL", "region": "Russia"},
        {"name": "Russia Sokol", "symbol": "SOKOL", "category": "INTERNATIONAL", "region": "Russia"},
        # Mexico
        {"name": "Mexico Maya", "symbol": "MAYA", "category": "INTERNATIONAL", "region": "Mexico"},
        {"name": "Mexico Isthmus", "symbol": "ISTHMUS", "category": "INTERNATIONAL", "region": "Mexico"},
        {"name": "Mexico Olmeca", "symbol": "OLMECA", "category": "INTERNATIONAL", "region": "Mexico"},
        # UAE
        {"name": "UAE Dubai", "symbol": "UAE-DUBAI", "category": "INTERNATIONAL", "region": "UAE"},
        {"name": "UAE Umm Shaif", "symbol": "UMM-SHAIF", "category": "INTERNATIONAL", "region": "UAE"},
        # Qatar
        {"name": "Qatar Marine", "symbol": "QATAR-MARINE", "category": "INTERNATIONAL", "region": "Qatar"},
        {"name": "Qatar Land", "symbol": "QATAR-LAND", "category": "INTERNATIONAL", "region": "Qatar"},
        # Iraq
        {"name": "Iraq Basrah Heavy", "symbol": "BASRAH-HEAVY", "category": "INTERNATIONAL", "region": "Iraq"},
        {"name": "Iraq Kirkuk", "symbol": "KIRKUK", "category": "INTERNATIONAL", "region": "Iraq"},
        # Saudi Arabia
        {"name": "Saudi Arab Medium", "symbol": "ARAB-MEDIUM", "category": "INTERNATIONAL", "region": "Saudi Arabia"},
        {"name": "Saudi Arab Heavy", "symbol": "ARAB-HEAVY", "category": "INTERNATIONAL", "region": "Saudi Arabia"},
        {"name": "Saudi Arab Extra Light", "symbol": "ARAB-XLIGHT", "category": "INTERNATIONAL", "region": "Saudi Arabia"},
        # Iran
        {"name": "Iran Light", "symbol": "IRAN-LIGHT", "category": "INTERNATIONAL", "region": "Iran"},
        {"name": "Iran Forozan Blend", "symbol": "FOROZAN", "category": "INTERNATIONAL", "region": "Iran"},
        # Nigeria
        {"name": "Nigeria Forcados", "symbol": "FORCADOS", "category": "INTERNATIONAL", "region": "Nigeria"},
        {"name": "Nigeria Qua Iboe", "symbol": "QUA-IBOE", "category": "INTERNATIONAL", "region": "Nigeria"},
        {"name": "Nigeria Brass River", "symbol": "BRASS-RIVER", "category": "INTERNATIONAL", "region": "Nigeria"},
        # Angola
        {"name": "Angola Cabinda", "symbol": "CABINDA", "category": "INTERNATIONAL", "region": "Angola"},
        {"name": "Angola Nemba", "symbol": "NEMBA", "category": "INTERNATIONAL", "region": "Angola"},
        # Australia
        {"name": "Australia Cossack", "symbol": "COSSACK", "category": "INTERNATIONAL", "region": "Australia"},
        {"name": "Australia Gippsland", "symbol": "GIPPSLAND", "category": "INTERNATIONAL", "region": "Australia"},
        # Azerbaijan
        {"name": "Azerbaijan Azeri BTC", "symbol": "AZERI-BTC", "category": "INTERNATIONAL", "region": "Azerbaijan"},
        # Brazil
        {"name": "Brazil Lula", "symbol": "LULA", "category": "INTERNATIONAL", "region": "Brazil"},
        # Kazakhstan
        {"name": "Kazakhstan CPC Blend", "symbol": "CPC-BLEND", "category": "INTERNATIONAL", "region": "Kazakhstan"},
        {"name": "Kazakhstan Tengiz", "symbol": "TENGIZ", "category": "INTERNATIONAL", "region": "Kazakhstan"},

        # ============================================================
        # CANADIAN BLENDS
        # ============================================================
        {"name": "Western Canadian Select", "symbol": "WCS", "category": "CANADIAN", "region": "Canada"},
        {"name": "Canadian Condensate", "symbol": "CAN-CONDENSATE", "category": "CANADIAN", "region": "Canada"},
        {"name": "Premium Synthetic", "symbol": "PREMIUM-SYNTH", "category": "CANADIAN", "region": "Canada"},
        {"name": "Sweet Synthetic", "symbol": "SWEET-SYNTH", "category": "CANADIAN", "region": "Canada"},
        {"name": "Peace Sour", "symbol": "PEACE-SOUR", "category": "CANADIAN", "region": "Canada"},
        {"name": "Central Alberta", "symbol": "CENTRAL-AB", "category": "CANADIAN", "region": "Canada"},
        {"name": "Cold Lake", "symbol": "COLD-LAKE", "category": "CANADIAN", "region": "Canada"},
        {"name": "Albian Heavy Synth", "symbol": "ALBIAN-HEAVY", "category": "CANADIAN", "region": "Canada"},

        # ============================================================
        # UNITED STATES BLENDS
        # ============================================================
        # Texas
        {"name": "WTI Midland", "symbol": "WTI-MIDLAND", "category": "US_BLEND", "region": "Texas"},
        {"name": "West Texas Sour", "symbol": "WTS", "category": "US_BLEND", "region": "Texas"},
        {"name": "Eagle Ford", "symbol": "EAGLE-FORD", "category": "US_BLEND", "region": "Texas"},
        {"name": "Texas Light Sweet (HLS)", "symbol": "HLS", "category": "US_BLEND", "region": "Texas"},
        # Louisiana
        {"name": "Louisiana Light Sweet", "symbol": "LLS", "category": "US_BLEND", "region": "Louisiana"},
        {"name": "Louisiana Eugene Island", "symbol": "EUGENE-ISLAND", "category": "US_BLEND", "region": "Louisiana"},
        {"name": "Louisiana Heavy Sweet", "symbol": "LHS", "category": "US_BLEND", "region": "Louisiana"},
        # Oklahoma
        {"name": "Oklahoma Sweet", "symbol": "OK-SWEET", "category": "US_BLEND", "region": "Oklahoma"},
        {"name": "Oklahoma Sour", "symbol": "OK-SOUR", "category": "US_BLEND", "region": "Oklahoma"},
        # Wyoming
        {"name": "Wyoming Sweet", "symbol": "WY-SWEET", "category": "US_BLEND", "region": "Wyoming"},
        {"name": "Wyoming Sour", "symbol": "WY-SOUR", "category": "US_BLEND", "region": "Wyoming"},
        {"name": "Wyoming Asphalt Sour", "symbol": "WY-ASPHALT", "category": "US_BLEND", "region": "Wyoming"},
        # Colorado
        {"name": "Colorado DJ Basin", "symbol": "DJ-BASIN", "category": "US_BLEND", "region": "Colorado"},
        # Nebraska
        {"name": "Nebraska Intermediate", "symbol": "NE-INTER", "category": "US_BLEND", "region": "Nebraska"},
        # Michigan
        {"name": "Michigan Sweet", "symbol": "MI-SWEET", "category": "US_BLEND", "region": "Michigan"},
        {"name": "Michigan Sour", "symbol": "MI-SOUR", "category": "US_BLEND", "region": "Michigan"},
        # Kansas
        {"name": "Kansas Common", "symbol": "KS-COMMON", "category": "US_BLEND", "region": "Kansas"},
        # Alaska
        {"name": "Alaska North Slope", "symbol": "ANS", "category": "US_BLEND", "region": "Alaska"},
        # Arkansas
        {"name": "Arkansas Sweet", "symbol": "AR-SWEET", "category": "US_BLEND", "region": "Arkansas"},
        # Mars
        {"name": "Mars Blend (Gulf)", "symbol": "MARS", "category": "US_BLEND", "region": "Gulf of Mexico"},
        {"name": "Poseidon (Gulf)", "symbol": "POSEIDON", "category": "US_BLEND", "region": "Gulf of Mexico"},
        {"name": "SGC (Gulf)", "symbol": "SGC", "category": "US_BLEND", "region": "Gulf of Mexico"},
        {"name": "Thunder Horse (Gulf)", "symbol": "THUNDER-HORSE", "category": "US_BLEND", "region": "Gulf of Mexico"},
    ]
    
    for comm_data in commodities:
        # Check if already exists
        exists = db.query(Commodity).filter(Commodity.symbol == comm_data["symbol"]).first()
        if not exists:
            logger.info(f"Adding {comm_data['name']} ({comm_data['symbol']})...")
            db.add(Commodity(**comm_data))
        else:
            logger.info(f"Updating metadata for {comm_data['name']}...")
            for key, value in comm_data.items():
                setattr(exists, key, value)
    
    db.commit()
    db.close()
    logger.info(f"Commodity seeding complete. {len(commodities)} benchmarks configured.")

if __name__ == "__main__":
    seed_commodities()
