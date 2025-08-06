from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer

def set_up_analyzer(morphology_db: str) -> Analyzer:
    # used to initialize an Analyzer with ADD_PROP backoff 
    # db = MorphologyDB.builtin_db('calima-msa-s31')
    db_type = None if morphology_db == 'r13' else morphology_db
    db = MorphologyDB.builtin_db(db_name=db_type)
    return Analyzer(db=db, backoff='ADD_PROP', cache_size=100000)