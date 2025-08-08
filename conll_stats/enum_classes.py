
from enum import Enum

class DataFrameStringHeaders(Enum):
    FILE_NAME = "file_name"

class WordLevelHeaders(Enum):
    WORD_COUNT = "word_count"
    TOKEN_COUNT = "token_count"
    TOKENIZED_WORD_COUNT = "tokenized_word_count"

class SentenceLevelHeaders(Enum):
    SENTENCE_COUNT = "sentence_count"
    MAX_SENTENCE_LENGTH = "max_sentence_length"
    MIN_SENTENCE_LENGTH = "min_sentence_length"
    MEAN_SENTENCE_LENGTH = "mean_sentence_length"

class PosTags(Enum):
    NOM = "NOM"
    PROP = "PROP"
    VRB = "VRB"
    VRBP_PASS = "VRB-PASS"
    PNX = "PNX"
    PRT = "PRT"
    FOREIGN = "FOREIGN"

class DeprelLabels(Enum):
    SBJ = "SBJ"
    OBJ = "OBJ"
    TPC = "TPC"
    PRD = "PRD"
    MOD = "MOD"
    IDF = "IDF"
    TMZ = "TMZ"
    FLAT = "---"

class LeadTypes(Enum):
    # whether child or parent leads the relationship
    P_C = "P-C"
    C_P = "C-P"