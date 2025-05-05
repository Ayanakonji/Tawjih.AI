import streamlit as st

st.set_page_config(page_title="Academic Orientation Bot", layout="centered")

st.title("🎓 AI Academic Orientation Advisor")
st.write("Answer a few quick questions and discover your best post-bac academic paths!")

# Initialize
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    #Diagnostic_Form
    with st.form("diagnostic_form"):
        name = st.text_input("👤 Your full name")
        city = st.text_input("📍 Your city")
        track = st.selectbox("🎓 Your baccalaureate track", [
            "Mathematical Science", "Physical Science", "Life & Earth Science",
            "Economics", "Technical Science"
        ])
        average = st.selectbox("📊 Your average (estimate)", [
            "≥ 16", "14–15.99", "12–13.99", "10-11.99"
        ])
        fav_subjects = st.multiselect("📘 Subjects you enjoy most (choose up to 2)", [
            "Mathematics", "Physics", "Biology", "Economics", "Agriculture"
        ])
        career = st.selectbox("💼 Your dream career", [
            "Engineer", "Doctor/Pharmacist", "Economist", "Veterinary Expert", "Technician"
        ])
        program_type = st.selectbox("🏫 Preferred program type", [
            "Competitive and theory-based", "Balanced academic + practical", "Hands-on and technical", "Specialized/professional"
        ])

        submitted = st.form_submit_button("Get My Orientation 🔍")

    if submitted:
        st.session_state.submitted = True
        st.session_state.answers = {
            "track": track,
            "average": average,
            "fav_subjects": fav_subjects,
            "career": career,
            "program_type": program_type
        }

else:
    st.subheader("📊 Your Top Orientation Matches")

    # === SCORING ===
    scores = {
        "CPGE": 0,
        "ENSA": 0,
        "ENSAM": 0,
        "IAV": 0,
        "FMP": 0,
        "ENCG": 0
    }

    ans = st.session_state.answers

    # --- Rule-Based Matching ---

    # Grades
    if ans["average"] == "≥ 16":
        scores["CPGE"] += 3
        scores["FMP"] += 3
        scores["ENSA"] += 3
        scores["ENSAM"] += 3
        scores["ENCG"] += 3
        scores["IAV"] += 3
    elif ans["average"] == "14–15.99":
        scores["CPGE"] += 2
        scores["FMP"] += 3
        scores["ENSA"] += 2
        scores["ENSAM"] += 2
        scores["ENCG"] += 2
        scores["IAV"] += 2
    elif ans["average"] == "12–13.99":
        scores["FMP"] += 2
        scores["ENSA"] += 1
        scores["ENSAM"] += 1
        scores["ENCG"] += 2
        scores["IAV"] += 2

    # Track Baccalaureate
    if "Science" in ans["track"]:
        scores["CPGE"] += 2
        scores["ENSA"] += 2
        scores["FMP"] += 1
        scores["ENSAM"] += 2
    if "Math" in ans["track"]:
        scores["CPGE"] += 3
        scores["ENSAM"] += 2
        scores["ENSA"] += 2
    if "Economics" in ans["track"]:
        scores["ENCG"] += 3

    # FAVORITE SUBJECTS
    for subj in ans["fav_subjects"]:
        if subj == "Mathematics":
            scores["CPGE"] += 2
            scores["ENSA"] += 2
            scores["ENSAM"] += 2
        elif subj == "Physics":
            scores["CPGE"] += 2
            scores["ENSAM"] += 2
            scores["ENSA"] += 2
        elif subj == "Biology":
            scores["FMP"] += 2
            scores["IAV"] += 2
        elif subj == "Economics":
            scores["ENCG"] += 3
        elif subj == "Engineering":
            scores["ENSA"] += 3
            scores["ENSAM"] += 3
        elif subj == "Agriculture":
            scores["IAV"] += 3

    # Career Goals
    if ans["career"] == "Engineer":
        scores["ENSA"] += 3
        scores["ENSAM"] += 3
        scores["CPGE"] += 1
    elif ans["career"] == "Doctor/Pharmacist":
        scores["FMP"] += 3
    elif ans["career"] == "Business Executive":
        scores["ENCG"] += 3
    elif ans["career"] == "Veterinary Expert":
        scores["IAV"] += 3
    elif ans["career"] == "Technician":
        scores["ENSAM"] += 2
        scores["ENSA"] += 2

    # Program Preference
    if ans["program_type"] == "Competitive and theory-based":
        scores["CPGE"] += 3
        scores["ENSA"] += 2
        scores["ENSAM"] += 2
    elif ans["program_type"] == "Hands-on and technical":
        scores["ENSAM"] += 2
        scores["ENSA"] += 1
    elif ans["program_type"] == "Balanced academic + practical":
        scores["IAV"] += 2
        scores["FMP"] += 1
    elif ans["program_type"] == "Specialized/professional":
        scores["IAV"] += 2
        scores["FMP"] += 2

    # --- Final Match Calculation ---
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    total_possible = max(sum(scores.values()), 1)

    for i, (school, score) in enumerate(sorted_scores[:3], start=1):
        percent = int((score / total_possible) * 100)
        st.markdown(f"### {i}. {school} — {percent}% Match")

    st.button("🔁 Start Again", on_click=lambda: st.session_state.clear())

