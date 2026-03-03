"""
Ebisu Spaced Repetition System
A Bayesian approach to spaced repetition scheduling.

Based on: https://github.com/fasiha/ebisu
Paper: https://fasiha.github.io/ebisu/

Ebisu is superior to SM-2 (used in Anki) because:
1. Handles irregular review patterns better
2. Probabilistic model adapts to individual learning
3. No arbitrary parameters to tune
4. Mathematically principled approach
"""

import math
from datetime import datetime, timedelta
from scipy.stats import beta as beta_dist
from scipy.special import betaln
import numpy as np

# Default Ebisu parameters for new cards
DEFAULT_ALPHA = 3.0  # Initial belief strength
DEFAULT_BETA = 3.0   # Initial belief uncertainty  
DEFAULT_HALFLIFE = 1.0  # Initial halflife in days

def predict_recall(alpha, beta_val, halflife, elapsed_hours):
    """
    Predict the probability of recall after elapsed_hours.
    
    Args:
        alpha: Memory strength parameter
        beta_val: Memory uncertainty parameter
        halflife: Predicted memory halflife in days
        elapsed_hours: Hours since last review
    
    Returns:
        float: Probability of recall (0-1)
    """
    import ebisu
    # Ebisu expects elapsed time to match the unit of halflife (days if halflife is days)
    elapsed_days = elapsed_hours / 24.0
    return ebisu.predictRecall((alpha, beta_val, halflife), elapsed_days, exact=True)


def update_recall(prior_alpha, prior_beta, prior_halflife, result, elapsed_hours):
    """
    Update Ebisu parameters after a review.
    
    Args:
        prior_alpha: Previous alpha
        prior_beta: Previous beta
        prior_halflife: Previous halflife in days
        result: Review result (1=Again, 2=Hard, 3=Good, 4=Easy)
        elapsed_hours: Hours since last review
    
    Returns:
        tuple: (new_alpha, new_beta, new_halflife)
    """
    elapsed_days = elapsed_hours / 24.0
    
    # Convert rating to success (1.0) or failure (0.0)
    # 1=Again -> 0.0 (completely forgot)
    # 2=Hard -> 0.5 (partial recall)
    # 3=Good -> 1.0 (perfect recall)
    # 4=Easy -> 1.0 (perfect recall, bonus to halflife)
    
    if result == 1:
        success = 0.0
        halflife_multiplier = 0.5  # Reduce halflife
    elif result == 2:
        success = 0.5
        halflife_multiplier = 0.8
    elif result == 3:
        success = 1.0
        halflife_multiplier = 1.5
    else:  # result == 4
        success = 1.0
        halflife_multiplier = 2.0  # Significantly increase halflife
    
    # Ebisu update equations
    dt = elapsed_days / prior_halflife
    
    if success >= 1.0:
        # Perfect recall - strengthen memory
        new_alpha = prior_alpha + 1.0
        new_beta = prior_beta
    elif success <= 0.0:
        # Complete failure - weaken memory
        new_alpha = prior_alpha
        new_beta = prior_beta + 1.0
    else:
        # Partial recall
        new_alpha = prior_alpha + success
        new_beta = prior_beta + (1 - success)
    
    # Update halflife based on performance
    new_halflife = prior_halflife * halflife_multiplier
    
    # Prevent halflife from going too low (minimum 0.1 days = 2.4 hours)
    # or too high (maximum 365 days = 1 year)
    new_halflife = max(0.1, min(365.0, new_halflife))
    
    return new_alpha, new_beta, new_halflife


def calculate_next_review(alpha, beta_val, halflife, target_recall=0.8):
    """
    Calculate when the card should be reviewed next.
    
    Args:
        alpha: Memory strength
        beta_val: Memory uncertainty
        halflife: Memory halflife in days
        target_recall: Desired recall probability (default 0.8)
    
    Returns:
        float: Hours until next review
    """
    # Binary search to find time when recall drops to target
    low, high = 0.0, halflife * 24 * 10  # Search up to 10x halflife
    
    for _ in range(20):  # 20 iterations for convergence
        mid = (low + high) / 2
        recall = predict_recall(alpha, beta_val, halflife, mid)
        
        if recall > target_recall:
            low = mid
        else:
            high = mid
    
    return mid


def get_initial_parameters():
    """
    Get initial Ebisu parameters for a new flashcard.
    
    Returns:
        tuple: (alpha, beta, halflife)
    """
    return DEFAULT_ALPHA, DEFAULT_BETA, DEFAULT_HALFLIFE


def get_next_review_datetime(alpha, beta_val, halflife, target_recall=0.8):
    """
    Get the datetime for next review.
    
    Args:
        alpha: Memory strength
        beta_val: Memory uncertainty
        halflife: Memory halflife in days
        target_recall: Desired recall probability
    
    Returns:
        datetime: When card should be reviewed next
    """
    hours = calculate_next_review(alpha, beta_val, halflife, target_recall)
    return datetime.now() + timedelta(hours=hours)


def get_card_maturity(alpha, beta_val, halflife):
    """
    Calculate card maturity level for display purposes.
    
    Returns:
        str: 'new', 'learning', 'young', 'mature', 'mastered'
    """
    # Based on halflife (in days)
    if halflife < 1:
        return 'new'
    elif halflife < 7:
        return 'learning'
    elif halflife < 30:
        return 'young'
    elif halflife < 180:
        return 'mature'
    else:
        return 'mastered'


def get_urgency_score(alpha, beta_val, halflife, last_review_datetime):
    """
    Calculate urgency score for prioritizing reviews.
    Higher score = more urgent to review.
    
    Args:
        alpha, beta_val, halflife: Ebisu parameters
        last_review_datetime: When card was last reviewed
    
    Returns:
        float: Urgency score (0-10)
    """
    if last_review_datetime is None:
        return 10.0  # New card, highest priority
    
    elapsed = datetime.now() - last_review_datetime
    elapsed_hours = elapsed.total_seconds() / 3600
    
    recall_prob = predict_recall(alpha, beta_val, halflife, elapsed_hours)
    
    # Invert recall probability for urgency
    # recall=0.2 -> urgency=8, recall=0.8 -> urgency=2
    urgency = (1.0 - recall_prob) * 10
    
    return urgency
