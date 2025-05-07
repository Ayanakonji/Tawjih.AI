import streamlit as st
import pandas as pd
import altair as alt
import json
from transformers import pipeline

# ------------------- App Configuration ------------------- #
st.set_page_config(page_title="Academic Orientation Bot", layout="centered")
st.title("🎓 AI Academic Orientation Advisor")

# ------------------- Language Selection ------------------- #
if "lang" not in st.session_state:
    lang = st.selectbox("🌐 Choose your language / Choisissez votre langue / اختر اللغة", ["English", "Français", "العربية"])
    if st.button("✅ Continue"):
        st.session_state.lang = lang
        st.session_state.submitted = False
        st.rerun()
else:
    lang = st.session_state.lang

    # ------------------- Translations ------------------- #
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

    # ------------------- Form Input ------------------- #
    if not st.session_state.get("submitted", False):
        with st.form("diagnostic_form"):
            name = st.text_input(t["name"])
            city = st.text_input(t["city"])
            track = st.selectbox(t["track"], ["Physics", "Math", "Economics", "Life and Earth Science"])
            average = st.selectbox(t["average"], ["≥ 16", "14–15.99", "12–13.99", "10-11.99"])
            fav_subjects = st.multiselect(t["subjects"], ["Mathematics", "Physics", "Biology", "Economics", "Agriculture"], max_selections=2)
            career = st.selectbox(t["career"], ["Engineer", "Doctor/Pharmacist", "Business Executive", "Veterinary Expert", "Technician"])
            program_type = st.selectbox(t["program"], ["Competitive and theory-based", "Hands-on and technical", "Balanced academic + practical", "Specialized/professional"])
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
            st.rerun()

    # ------------------- Orientation Results ------------------- #
    else:
        st.subheader(t["result"])
        scores = {"CPGE": 0, "ENSA": 0, "ENSAM": 0, "IAV": 0, "FMP": 0, "ENCG": 0}
        ans = st.session_state.answers

        # Average-based score adjustment
        if ans["average"] == "≥ 16":
            for k in scores: scores[k] += 3
        elif ans["average"] == "14–15.99":
            scores.update({"CPGE": 2, "FMP": 3, "ENSA": 2, "ENSAM": 2, "ENCG": 3, "IAV": 3})
        elif ans["average"] == "12–13.99":
            scores.update({"FMP": 3, "ENSA": 1, "ENSAM": 1, "ENCG": 3, "IAV": 3})
        elif ans["average"] == "10-11.99":
            for k in scores: scores[k] += 1

        # Track
        if "Physics" in ans["track"]:
            scores["CPGE"] += 2; scores["ENSA"] += 2; scores["FMP"] += 1; scores["ENSAM"] += 2; scores["IAV"] += 2
        if "Math" in ans["track"]:
            scores["CPGE"] += 3; scores["ENSAM"] += 3; scores["ENSA"] += 3
        if "Economics" in ans["track"]:
            scores["ENCG"] += 3

        # Subjects
        for subj in ans["fav_subjects"]:
            match subj:
                case "Mathematics": scores["CPGE"] += 2; scores["ENSA"] += 2; scores["ENSAM"] += 2
                case "Physics": scores["CPGE"] += 2; scores["ENSA"] += 2; scores["ENSAM"] += 2
                case "Biology": scores["FMP"] += 3; scores["IAV"] += 3
                case "Economics": scores["ENCG"] += 3
                case "Agriculture": scores["IAV"] += 3

        # Dream Career
        match ans["career"]:
            case "Engineer": scores["ENSA"] += 3; scores["ENSAM"] += 3; scores["CPGE"] += 2
            case "Doctor/Pharmacist": scores["FMP"] += 3
            case "Business Executive": scores["ENCG"] += 3
            case "Veterinary Expert": scores["IAV"] += 3
            case "Technician": scores["ENSAM"] += 2; scores["ENSA"] += 2

        # Preferred Program Type
        match ans["program_type"]:
            case "Competitive and theory-based": scores["CPGE"] += 3; scores["ENSA"] += 2; scores["ENSAM"] += 2
            case "Hands-on and technical": scores["ENSAM"] += 2; scores["ENSA"] += 2
            case "Balanced academic + practical": scores["IAV"] += 2; scores["FMP"] += 1
            case "Specialized/professional": scores["IAV"] += 2; scores["FMP"] += 2

        # Display results
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_score = sorted_scores[0][1]
        for i, (school, score) in enumerate(sorted_scores[:3], 1):
            percent = int((score / top_score) * 100)
            st.markdown(f"### {i}. {school} — {percent}% Match")

        st.button(t["again"], on_click=lambda: st.session_state.clear())

        # Bar chart
        st.subheader("📊 Orientation Score Breakdown")
        df = pd.DataFrame(scores.items(), columns=["School", "Score"])
        chart = alt.Chart(df).mark_bar(color="#4e79a7").encode(
            x=alt.X("School", sort="-y"),
            y="Score",
            tooltip=["School", "Score"]
        ).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)

        # ------------------- Extra Info Section ------------------- #
        if "show_extra" not in st.session_state:
            st.session_state.show_extra = False
        if not st.session_state.show_extra:
            if st.button("📄 More Informations:"):
                st.session_state.show_extra = True
                st.rerun()

        if st.session_state.show_extra:
            st.subheader("📄 More Information Assistant")
            st.write("You can now ask any question about the programs like CPGE, ENSA, FMP, etc.")

            @st.cache_data
            def load_school_data(json_path="moroccan_higher_education_programs(1).json"):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except FileNotFoundError:
                    st.error("Education program data file not found.")
                    return {}

            @st.cache_resource
            def get_pipelines():
                qa = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
                summarizer = pipeline("text2text-generation", model="t5-small")
                return qa, summarizer

            school_data = load_school_data()
            qa_pipeline, summarizer = get_pipelines()

            user_question = st.text_input("🧐 Ask a question about the schools")
            if user_question:
                with st.spinner("Searching for the best answer..."):
                    best_answer = None
                    best_score = 0
                    for school, data in school_data.items():
                        context = f"{school}: {data.get('Presentation','')} Programmes : {', '.join(data.get('Programmes', []))} Modalites_Inscription : {data.get('Modalites_Inscription', {}).get('Conditions','')} {data.get('Modalites_Inscription', {}).get('Procedure','')} Perspectives_Carriere : {', '.join(data.get('Perspectives_Carriere', []))}"
                        result = qa_pipeline(question=user_question, context=context)
                        if result['score'] > best_score and result['score'] > 0.3:
                            best_score = result['score']
                            best_answer = result['answer']

                    if best_answer:
                        reformulated = summarizer(f"summarize: {best_answer}")[0]['generated_text']
                        st.success(f"💬 {reformulated}")
                    else:
                        st.error("Sorry, I couldn't find a good answer for that question.")
