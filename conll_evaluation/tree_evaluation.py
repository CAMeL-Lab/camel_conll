import pandas as pd

from conllx_df.conllx_df import ConllxDf
from conll_evaluation.tokens_to_words import get_unsegmented_words
from conll_evaluation.align_trees import align_trees


def evaluate_tree_tokens(ref_tree_tokens, pred_tree_tokens, total_ref_tree_token_count, total_pred_tree_token_count):
    # ref_tree and pred_tree have already been aligned
    # the original token counts are required to calculate the f1 score

    token_matches = (ref_tree_tokens == pred_tree_tokens).sum()

    token_recall = token_matches / total_ref_tree_token_count
    token_precision = token_matches / total_pred_tree_token_count
    f1_score = (2*token_precision*token_recall / (token_precision+token_recall))
    return {
        'tokenization_f1_score': f1_score*100,
        'tokenization_recall': token_recall*100,
        'tokenization_precision': token_precision*100,
    }

def evaluate_words(gold_column, pred_column):
    """
    """
    gold_words = pd.DataFrame(get_unsegmented_words(gold_column.tolist()), columns=['FORM'])
    pred_words = pd.DataFrame(get_unsegmented_words(pred_column.tolist()), columns=['FORM'])
    # using align_trees on dataframe containing only form. if tokens are inserted the dataframe will contain all conll headers
    gold_aligned, pred_aligned = align_trees(gold_words, pred_words)

    return (gold_aligned.FORM == pred_aligned.FORM).sum() / gold_words.shape[0]

def evaluate_columns(column_1, column_2, column_count, perfectly_parsed=False):
    if perfectly_parsed:
        return 100 * int((column_1 == column_2).all())

    return 100 * ((column_1 == column_2).sum() / column_count)

def evaluate_las(ref_tree, pred_tree, total_ref_tree_token_count, perfectly_parsed=False):
    if perfectly_parsed:
        return 100 * int(((ref_tree['HEAD'] == pred_tree['HEAD']) & (ref_tree['DEPREL'] == pred_tree['DEPREL'])).all())
    
    return 100 * (((ref_tree['HEAD'] == pred_tree['HEAD']) & (ref_tree['DEPREL'] == pred_tree['DEPREL'])).sum() / total_ref_tree_token_count)

def evaluate_word_accuracy(ref_conll, pred_conll):
    scores = []
    for i in range(ref_conll.get_sentence_count()):
        gold_df = ref_conll.get_df_by_id(i)
        pred_df = pred_conll.get_df_by_id(i)
        scores.append({
            'word_accuracy': evaluate_words(gold_df['FORM'], pred_df['FORM']) * 100
        })
    return pd.DataFrame(scores).mean().to_dict()

def evaluate_perfectly_parsed_trees(aligned_df_gold_list, aligned_df_pred_list):
    scores = []
    for gold_df, pred_df in zip(aligned_df_gold_list, aligned_df_pred_list):
        scores.append({
            'pp_label_score': evaluate_columns(gold_df['DEPREL'], pred_df['DEPREL'], 0, True),
            'pp_uas_score': evaluate_columns(gold_df['HEAD'], pred_df['HEAD'], 0, True),
            'pp_las_score': evaluate_las(gold_df, pred_df, 0, True)
        })
    return pd.DataFrame(scores).mean().to_dict()

def get_aligned_trees(ref_conll, pred_conll):
    aligned_df_gold_list = []
    aligned_df_pred_list = []

    total_ref_tree_token_count = 0
    total_pred_tree_token_count = 0
    for i in range(ref_conll.get_sentence_count()):
        ref_tree = ref_conll.get_df_by_id(i)
        pred_tree = pred_conll.get_df_by_id(i)
        total_ref_tree_token_count += ref_tree.shape[0]
        total_pred_tree_token_count += pred_tree.shape[0]
        
        ref_tree_aligned, pred_tree_aligned = align_trees(ref_tree, pred_tree)
        aligned_df_gold_list.append(ref_tree_aligned)
        aligned_df_pred_list.append(pred_tree_aligned)
    
    return aligned_df_gold_list, aligned_df_pred_list, total_ref_tree_token_count, total_pred_tree_token_count

def compare_conll_trees(ref_conll: ConllxDf, pred_conll: ConllxDf):
    assert ref_conll.get_sentence_count() == pred_conll.get_sentence_count()

    aligned_df_gold_list, aligned_df_pred_list, total_ref_tree_token_count, total_pred_tree_token_count = get_aligned_trees(ref_conll, pred_conll)
    gold_df = pd.concat(aligned_df_gold_list)
    pred_df = pd.concat(aligned_df_pred_list)
    
    # f1_score, precision, and recall
    tokenization_scores = evaluate_tree_tokens(gold_df.FORM, pred_df.FORM, total_ref_tree_token_count, total_pred_tree_token_count)
    word_accuracy = evaluate_word_accuracy(ref_conll, pred_conll)
    pos_score = {'pos': evaluate_columns(gold_df['UPOS'], pred_df['UPOS'], total_ref_tree_token_count)}
    
    attachment_scores = {
        'label_score': evaluate_columns(gold_df['DEPREL'], pred_df['DEPREL'], total_ref_tree_token_count),
        'uas_score': evaluate_columns(gold_df['HEAD'], pred_df['HEAD'], total_ref_tree_token_count),
        'las_score': evaluate_las(gold_df, pred_df, total_ref_tree_token_count)
    }

    perfectly_parsed = evaluate_perfectly_parsed_trees(aligned_df_gold_list, aligned_df_pred_list)

    # converting to pandas and manually setting values to be able to use numpys round function later
    scores_combined = {**tokenization_scores, **pos_score, **attachment_scores, **perfectly_parsed, **word_accuracy}
    final_scores = pd.Series(scores_combined)
    return {
        'tokenization_f1_score': final_scores.tokenization_f1_score,
        'tokenization_precision': final_scores.tokenization_precision,
        'tokenization_recall': final_scores.tokenization_recall,
        'word_accuracy': final_scores.word_accuracy,
        'pos': final_scores.pos,
        'uas_score': final_scores.uas_score,
        'label_score': final_scores.label_score,
        'las_score': final_scores.las_score,
        'pp_uas_score': final_scores.pp_uas_score,
        'pp_label_score': final_scores.pp_label_score,
        'pp_las_score': final_scores.pp_las_score
    }

