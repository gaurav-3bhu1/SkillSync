from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data_loader import (
    load_jobs,
    load_courses,
    load_skills,
)
from src.hybrid_skill_extractor import (
    HybridSkillExtractor,
)
from src.hybrid_job_skill_mapper import (
    build_hybrid_job_skill_mapping,
)


@st.cache_resource
def get_hybrid_extractor() -> HybridSkillExtractor:
    """
    Load the embedding model exactly once per Streamlit
    process/session lifecycle.
    """

    skills = load_skills()

    return HybridSkillExtractor(
        skills
    )


@st.cache_data
def get_hybrid_job_skill_mapping() -> pd.DataFrame:
    """
    Build and cache the hybrid job-skill mapping.
    """

    jobs = load_jobs()
    extractor = get_hybrid_extractor()

    return build_hybrid_job_skill_mapping(
        jobs,
        extractor,
    )


@st.cache_data
def get_courses() -> pd.DataFrame:
    """
    Load and cache the course dataset.
    """

    return load_courses()


@st.cache_data
def get_jobs() -> pd.DataFrame:
    """
    Load and cache the raw job dataset.
    """

    return load_jobs()