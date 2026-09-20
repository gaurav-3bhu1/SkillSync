import streamlit as st

from dashboard.market_page import render as render_market
from dashboard.trends_page import render as render_trends
from dashboard.course_page import render as render_course
from dashboard.district_page import (
    render as render_district
)

st.set_page_config(
    page_title="SkillSync",
    page_icon="🎯",
    layout="wide",
)


def main():
    st.sidebar.title("SkillSync")

    st.sidebar.caption(
        "Labour-market intelligence and "
        "curriculum alignment"
    )

    page = st.sidebar.radio(
        "Navigate",
        [
            "Market Intelligence",
            "Course Alignment",
            "Skill Trends",
            "District Planning",
        ],
    )

    if page == "Market Intelligence":
        render_market()

    elif page == "Skill Trends":
        render_trends()

    elif page == "Course Alignment":
        render_course()

    elif page == "District Planning":
        render_district()


if __name__ == "__main__":
    main()