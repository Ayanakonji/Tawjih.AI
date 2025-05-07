import streamlit as st
import pandas as pd
import altair as alt
import json
from transformers import pipeline
import re

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
            # Load the JSON file
                with open("moroccan_higher_education_programs(1).json", "r", encoding="utf-8") as f:
                    data = json.load(f)

            st.set_page_config(page_title="Chatbot d'Orientation", layout="wide")

            st.title("🤖 Academic Orientation Chatbot")
            st.write("Posez votre question sur les écoles supérieures marocaines (FR/AR/EN)")

            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []

            # Detect institution
            def find_institution(user_input):
                for name in data:
                    if re.search(rf"\b{name}\b", user_input, re.IGNORECASE):
                        return name
                return None

            # Detect language
            def detect_language(text):
                try:
                    return detect(text)
                except:
                    return "en"

            # Response builder
            def get_response(user_input, lang):
                institution = find_institution(user_input)
                if not institution:
                    return {
                        "en": "❓ I couldn't identify the institution. Try 'ENSA', 'FMP', etc.",
                        "fr": "❓ Je n’ai pas reconnu l’établissement. Essayez avec ‘ENSA’, ‘FMP’, etc.",
                        "ar": "❓ لم أتمكن من تحديد المؤسسة. جرب استخدام أسماء مثل 'ENSA' أو 'FMP'."
                    }.get(lang, "Sorry, I couldn’t understand.")
    
                info = data[institution]
    
                if lang == "fr":
                    response = f"🏫 **{institution}**\n\n"
                    response += f"📘 *{info.get('Presentation', '')}*\n\n"

                    # Programmes
                    response += "**📚 Programmes :**\n"
                    prog = info.get("Programmes")
                    if isinstance(prog, list):
                        response += "\n".join(f"- {p}" for p in prog)
                    elif isinstance(prog, dict):
                        for cat, items in prog.items():
                            response += f"**{cat}**\n"
                            if isinstance(items, list):
                                response += "\n".join(f"- {i}" for i in items) + "\n"
                            else:
                                response += f"- {items}\n"

                    modalites = info.get("Modalites_Inscription", {})
                    response += f"\n**📝 Admission :**\n- Conditions : {modalites.get('Conditions', '')}\n- Procédure : {modalites.get('Procedure', '')}\n"

                    careers = info.get("Perspectives_Carriere", [])
                    if careers:
                        response += "\n**💼 Débouchés :**\n" + "\n".join(f"- {c}" for c in careers)

                    response += f"\n\n**📍 Localisation :** {info.get('Localisation', '')}"
                    return response

                elif lang == "ar":
                    response = f"🏫 **{institution}**\n\n"
                    response += f"📘 {info.get('Presentation', '')}\n\n"

                    response += "**📚 البرامج:**\n"
                    prog = info.get("Programmes")
                    if isinstance(prog, list):
                        response += "\n".join(f"- {p}" for p in prog)
                    elif isinstance(prog, dict):
                        for cat, items in prog.items():
                            response += f"**{cat}**\n"
                            if isinstance(items, list):
                                response += "\n".join(f"- {i}" for i in items) + "\n"
                            else:
                                response += f"- {items}\n"

                    modalites = info.get("Modalites_Inscription", {})
                    response += f"\n**📝 شروط القبول:**\n- الشروط: {modalites.get('Conditions', '')}\n- الإجراءات: {modalites.get('Procedure', '')}\n"

                    careers = info.get("Perspectives_Carriere", [])
                    if careers:
                        response += "\n**💼 الآفاق المهنية:**\n" + "\n".join(f"- {c}" for c in careers)

                    response += f"\n\n**📍 المكان:** {info.get('Localisation', '')}"
                    return response

                else:  # English fallback
                    response = f"🏫 **{institution}**\n\n"
                    response += f"📘 *{info.get('Presentation', '')}*\n\n"
                    response += "**📚 Programs:**\n"
                    prog = info.get("Programmes")
                    if isinstance(prog, list):
                        response += "\n".join(f"- {p}" for p in prog)
                    elif isinstance(prog, dict):
                        for cat, items in prog.items():
                            response += f"**{cat}**\n"
                            if isinstance(items, list):
                                response += "\n".join(f"- {i}" for i in items) + "\n"
                            else:
                                response += f"- {items}\n"

                    modalites = info.get("Modalites_Inscription", {})
                    response += f"\n**📝 Admission:**\n- Conditions: {modalites.get('Conditions', '')}\n- Procedure: {modalites.get('Procedure', '')}\n"

                    careers = info.get("Perspectives_Carriere", [])
                    if careers:
                        response += "\n**💼 Career Opportunities:**\n" + "\n".join(f"- {c}" for c in careers)

                    response += f"\n\n**📍 Location:** {info.get('Localisation', '')}"
                    return response

            # Input area
            st.chat_message("assistant").markdown("👋 Bonjour ! Posez une question comme : _“Qu’est-ce que l’ENCG ?”_ ou _“What can I study at ENSAM?”_")

            user_input = st.chat_input("Tapez votre question ici...")

            if user_input:
                lang = detect_language(user_input)
                response = get_response(user_input, lang)

                # Save and show user message
                st.session_state.chat_history.append(("user", user_input))
                with st.chat_message("user", avatar="🧑"):
                    st.markdown(user_input)

                # Save and show bot response
                st.session_state.chat_history.append(("bot", response))
                with st.chat_message("assistant", avatar="🎓"):
                    st.markdown(response)

            # Show past chat
            for role, msg in st.session_state.chat_history:
                avatar = "🧑" if role == "user" else "🎓"
                with st.chat_message(role, avatar=avatar):
                    st.markdown(msg)

                            

            else:
                st.write("How do you rate the result of the first diagnostic test")
                rate = st.radio("Rate", ["1", "2", "3", "4", "5"])
                st.button("Go back to the first diagnostic test", on_click=lambda: st.session_state.clear())