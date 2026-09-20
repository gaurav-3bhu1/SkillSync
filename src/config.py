"""
Central configuration for SkillSync.
"""

# Selected through the prototype threshold sweep.
# This value should be re-evaluated when the validation
# dataset is expanded.
SEMANTIC_THRESHOLD = 0.55

# Number of semantic candidates considered per text.
SEMANTIC_TOP_K = 3