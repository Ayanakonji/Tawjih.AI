import streamlit as st
import pandas as pd
import altair as alt
import json
from transformers import pipeline
import sys

st.set_page_config(page_title="Academic Orientation Bot", layout="centered")
st.title("🎓 AI Academic Orientation Advisor")

# Step 1: Language selection
if "lang" not in st.session_state:
    lang = st.selectbox("🌐 Choose your language / Choisissez votre langue / اختر اللغة", ["English", "Français", "العربية"])
    if st.button("✅ Continue"):
        st.session_state.lang = lang
        st.session_state.submitted = False  # Reset any previous form submission
        st.rerun()
else:
    lang = st.session_state.lang

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

    if not st.session_state.get("submitted", False):
        with st.form("diagnostic_form"):
            name = st.text_input(t["name"])
            city = st.text_input(t["city"])
            track = st.selectbox(t["track"], ["Physics", "Math", "Economics","Life and Earth Science"])
            average = st.selectbox(t["average"], ["≥ 16", "14–15.99", "12–13.99", "10-11.99"])
            fav_subjects = st.multiselect(t["subjects"], ["Mathematics", "Physics", "Biology", "Economics", "Agriculture"])
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

    else:
        st.subheader(t["result"])

        # Score System
        scores = {
            "CPGE": 0,
            "ENSA": 0,
            "ENSAM": 0,
            "IAV": 0,
            "FMP": 0,
            "ENCG": 0
        }

        ans = st.session_state.answers

        if ans["average"] == "≥ 16":
            for k in scores: scores[k] += 3
        elif ans["average"] == "14–15.99":
            scores.update({"CPGE": 2, "FMP": 3, "ENSA": 2, "ENSAM": 2, "ENCG": 3, "IAV": 3})
        elif ans["average"] == "12–13.99":
            scores.update({"FMP": 3, "ENSA": 1, "ENSAM": 1, "ENCG": 3, "IAV": 3})
        elif ans["average"] == "10-11.99":
            for k in scores: scores[k] += 1

        if "Physics" in ans["track"]:
            scores["CPGE"] += 2; scores["ENSA"] += 2; scores["FMP"] += 1; scores["ENSAM"] += 2; scores["IAV"] += 2
        if "Math" in ans["track"]:
            scores["CPGE"] += 3; scores["ENSAM"] += 3; scores["ENSA"] += 3
        if "Economics" in ans["track"]:
            scores["ENCG"] += 3

        for subj in ans["fav_subjects"]:
            match subj:
                case "Mathematics": scores["CPGE"] += 2; scores["ENSA"] += 2; scores["ENSAM"] += 2
                case "Physics": scores["CPGE"] += 2; scores["ENSA"] += 2; scores["ENSAM"] += 2
                case "Biology": scores["FMP"] += 3; scores["IAV"] += 3
                case "Economics": scores["ENCG"] += 3
                case "Agriculture": scores["IAV"] += 3

            match ans["career"]:
                case "Engineer": scores["ENSA"] += 3; scores["ENSAM"] += 3; scores["CPGE"] += 2
                case "Doctor/Pharmacist": scores["FMP"] += 3
                case "Business Executive": scores["ENCG"] += 3
                case "Veterinary Expert": scores["IAV"] += 3
                case "Technician": scores["ENSAM"] += 2; scores["ENSA"] += 2

            match ans["program_type"]:
                case "Competitive and theory-based": scores["CPGE"] += 3; scores["ENSA"] += 2; scores["ENSAM"] += 2
                case "Hands-on and technical": scores["ENSAM"] += 2; scores["ENSA"] += 2
                case "Balanced academic + practical": scores["IAV"] += 2; scores["FMP"] += 1
                case "Specialized/professional": scores["IAV"] += 2; scores["FMP"] += 2

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        total = max(sum(scores.values()), 1)
        for i, (school, score) in enumerate(sorted_scores[:3], 1):
            percent = int((score / total) * 100)
            st.markdown(f"### {i}. {school} — {percent}% Match")

        st.button(t["again"], on_click=lambda: st.session_state.clear())

        # Display the scores in a bar chart
        st.subheader("📈 Orientation Score Breakdown")
        df = pd.DataFrame(scores.items(), columns=["School", "Score"])
        chart = alt.Chart(df).mark_bar(color="#4e79a7").encode(
            x=alt.X("School", sort="-y"),
            y="Score",
            tooltip=["School", "Score"]
        ).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)
        # Add a button to show extra diagnostic
        if "show_extra" not in st.session_state:
            st.session_state.show_extra = False
        if not st.session_state.show_extra:
            if st.button("📄 More Informations:"):
                st.session_state.show_extra = True
                st.rerun()
        if st.session_state.show_extra:
            st.subheader("More Informations:")
            st.write("Agree to know more informations to deeply know about your choice, if you are then select yes, if it isn't then select no")
            more_information = st.radio("Do you want to know more informations about your choices", ["Yes", "No"])
            if more_information == "Yes":
                qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad", tokenizer="distilbert-base-cased-distilled-squad")
                summarizer = pipeline("text2text-generation", model="t5-small", tokenizer="t5-small")  # Utilisation de T5 pour reformuler
                # Load the JSON file
                def load_school_data(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        return json.load(f)

                def reformulate_answer(answer):
                    input_text = f"summarize: {answer}"
                    result = summarizer(input_text)
                    return result[0]['generated_text']
                def answer_question_with_reformulating(school_data,question):
                    for school, data in school_data.items():
                        # Reformulate the text
                        context = f"{school}: {data.get('Presentation','')} Programmes : {', '.join(data.get('programmes', []))} Modalites_Inscription : {', '.join(data.get('Modalites_Inscription', []))} Perspectives_Carriere : {', '.join(
                        data.get('Perspectives_Carriere', []))} Localisation : {', '.join(data.get('Localisation', []))}" 
                        result = qa_pipeline(question=question, context=context)
                        if result['score'] > 0.3:
                            return result['answer']
                def main():
                    st.title("Academic Orientation Bot")
                    json_path = "moroccan_higher_education_programs(1).json"
                    school_data = load_school_data(json_path)
                    question = st.text_input("Ask a question about the schools","")
                    if question:
                        with st.spinner("Searching for an answer..."):
                            answer = answer_question_with_reformulating(school_data, question)
                            st.write("Answer:", answer)
                if __name__ == "__main__":
                    main()
                            

            else:
                st.write("How do you rate the result of the first diagnostic test")
                rate = st.selectbox("Rate", ["1", "2", "3", "4", "5"])
                st.button("Go back to the first diagnostic test", on_click=lambda: st.session_state.clear())
                
            # What i am gonna do is to make two condionals if it yes then i will add the extra diagnostic questions if it no then i will make a question 
            # how do u rate the result of the first diagnostic test and i will add a button to go back to the first diagnostic test
            # for the yes response depends on the answer of the question i will make a diagnostic test to reveal his own speciality in the school he choosed then
            # the test will end and i will ask him to rate the service and make a comments bar to leave a comment about the service
            # this is the first service of my platform and i will add the map of the schools in morooco and the contact of the schools
            # the third service is to make a chatbot in whatssap,telegram that had documentations about the tests to admission to the schools
            
            
           