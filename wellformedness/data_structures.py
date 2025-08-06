"""

token-level error example:
{
    'token_id': 9,
    'flagged_issue': 'FLAG_UNK_SYNTAX_PATTERN',
    'sentence_number': 3,
    'form': 'يرى',
    'pos_tag': 'VRB-PASS',
    'label': 'MOD',
    'parent_id': 8,
    'parent_form': '+ما',
    'parent_pos_tag': '#NOM',
    'direction': 'P-C'
    'text': 'مـا أبـصـرت عـينـاك أحـســـن مـــنـــظـــر فـــيمـــا يرى مـــــن ســـــــائر الأشـــــــياء',
}

sentence-level error example:
{
    'flagged_issue': 'FLAG_NONPROJECTIVE',
    'sentence_number': 5
    'text': 'لم يمش من يابس يوماً ولا وحل إلا بنور هداه تقى الزلقا',
}


"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class IssueType(Enum):
    FLAG_ENCLITIC = "FLAG_ENCLITIC"
    FLAG_PROCLITIC = "FLAG_PROCLITIC"
    FLAG_ID_OR_HEAD = "FLAG_ID_OR_HEAD"
    FLAG_MULTIPLE_DEPREL_LABELS = "FLAG_MULTIPLE_DEPREL_LABELS"
    FLAG_CATIB_TAGS = "FLAG_CATIB_TAGS"
    FLAG_DEPREL_LABELS = "FLAG_DEPREL_LABELS"
    FLAG_FORM_OOV = "FLAG_FORM_OOV"
    FLAG_FORM_POS_MISMATCH = "FLAG_FORM_POS_MISMATCH"
    FLAG_MID_PNX_ATT = "FLAG_MID_PNX_ATT"
    FLAG_SENTENCE_NUM = "FLAG_SENTENCE_NUM"
    FLAG_UNK_SYNTAX_PATTERN = "FLAG_UNK_SYNTAX_PATTERN"
    FLAG_PNX_POSITION = "FLAG_PNX_POSITION"
    FLAG_NONPROJECTIVE = "FLAG_NONPROJECTIVE"
    FLAG_ROOT_ATT = "FLAG_ROOT_ATT"

class CatibTag(Enum):
    NOM = 'NOM'
    PROP = 'PROP'
    VRB = 'VRB'
    VRB_PASS = 'VRB-PASS'
    PRT = 'PRT'
    PNX = 'PNX'
    FOREIGN = 'FOREIGN'
    
    def is_valid_tag(self, tag):
        return tag.replace('-', '_') in CatibTag.__members__
    
class DeprelLabel(Enum):
    SBJ = 'SBJ'
    OBJ = 'OBJ'
    TPC = 'TPC'
    PRD = 'PRD'
    IDF = 'IDF'
    TMZ = 'TMZ'
    MOD = 'MOD'
    FLAT = '---'


class FlaggedIssue(ABC):
    @abstractmethod
    def to_dict(self):
        """Converts issue to a dictionary"""

@dataclass
class TokenFlaggedIssue(FlaggedIssue):
    token_id: int
    issue_type: IssueType
    sentence_number: int
    
    form: str
    pos_tag: str
    label: DeprelLabel
    
    parent_id: int
    parent_form: str
    parent_pos_tag: str
    
    direction: str
    text: str
    
    def to_dict(self):
        return {
            "token_id": self.token_id,
            "issue_type": self.issue_type,
            "sentence_number": self.sentence_number,
            "form": self.form,
            "pos_tag": self.pos_tag,
            "label": self.label,
            "parent_id": self.parent_id,
            "parent_form": self.parent_form,
            "parent_pos_tag": self.parent_pos_tag,
            "direction": self.direction,
            "text": self.text,
            }
@dataclass
class SentenceFlaggedIssue(FlaggedIssue):
    issue_type: IssueType
    sentence_number: int
    text: str
    
    def to_dict(self):
        return {
            "issue_type": self.issue_type,
            "sentence_number": self.sentence_number,
            "text": self.text,
            }