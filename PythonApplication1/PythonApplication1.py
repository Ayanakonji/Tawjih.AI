import streamlit as st
import pandas as pd
import altair as alt
st.set_page_config(page_title="Academic Orientation Bot", layout="centered")

st.title("🎓 AI Academic Orientation Advisor")

lang = st.selectbox("🌐 Choose your language / Choisissez votre langue / اختر اللغة", ["English", "Français","العربية"])
translations = {
    "English": {
        "name": "👤 Your full name",
        "city": "📍 Your city",
        "track": "🎓 Your baccalaureate track",
        "average": "📊 Your average (estimate)",
        "subjects": "📘 Subjects you enjoy most (choose up to 2)",
        "career": "💼 Your dream career",
        "program": "🏫 Preferred program type",
        "submit": "Get My Orientation 🔍",
        "result": "📊 Your Top Orientation Matches",
        "again": "🔁 Start Again"
    },
    "Français": {
        "name": "👤 Votre nom complet",
        "city": "📍 Votre ville",
        "track": "🎓 Votre filière du bac",
        "average": "📊 Votre moyenne (estimation)",
        "subjects": "📘 Matières préférées (choisissez jusqu’à 2)",
        "career": "💼 Métier de rêve",
        "program": "🏫 Type de programme souhaité",
        "submit": "Obtenir mon orientation 🔍",
        "result": "📊 Vos meilleures orientations",
        "again": "🔁 Recommencer"
    },
    "العربية": {
        "name": "👤 الاسم الكامل",
        "city": "📍 المدينة",
        "track": "🎓 شعبة البكالوريا",
        "average": "📊 المعدل التقديري",
        "subjects": "📘 المواد المفضلة (اختر اثنين)",
        "career": "💼 المهنة التي تحلم بها",
        "program": "🏫 نوع البرنامج المفضل",
        "submit": "احصل على توجيهي 🔍",
        "result": "📊 أفضل التخصصات المناسبة لك",
        "again": "🔁 ابدأ من جديد"
    }
}
t = translations[lang]

# Initialize
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if not st.session_state.submitted:
    #Diagnostic_Form
    st.write("Answer a few quick questions and discover your best post-bac academic paths!")
    with st.form("diagnostic_form"):
        name = st.text_input(t["name"])
        city = st.text_input(t["city"])
        track = st.selectbox(t["city"])
        average = st.selectbox(t["average"])
        fav_subjects = st.multiselect(t["subjects"])
        career = st.selectbox(t["career"])
        program_type = st.selectbox(t["program"])

        submitted = st.form_submit_button(t["submit"])

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
    st.subheader(t["result"])

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
        scores["ENCG"] += 3
        scores["IAV"] += 3
    elif ans["average"] == "12–13.99":
        scores["FMP"] += 3
        scores["ENSA"] += 1
        scores["ENSAM"] += 1
        scores["ENCG"] += 3
        scores["IAV"] += 3

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

    st.button(t["again"], on_click=lambda: st.session_state.clear())

    st.subheader("📈 Orientation Score Breakdown")
    # Display the scores in a bar chart
    df = pd.DataFrame(scores.items(), columns=["School","Score"])
    bar_chart = alt.Chart(df).mark_bar(color="#4e79a7").encode(
    x=alt.X("School", sort="-y"),
    y="Score",
    tooltip=["School", "Score"]
).properties(
    width=600,
    height=400,
    title="Your Orientation Match Scores"
)
    st.altair_chart(bar_chart, use_container_width=True)


