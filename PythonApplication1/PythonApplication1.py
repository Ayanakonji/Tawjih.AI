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
                # Load JSON data
                if "last_institution" not in st.session_state:
                    st.session_state.last_institution = None
                with open("moroccan_higher_education_programs(1).json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                st.title("🎓 Moroccan Academic Orientation Chatbot")
                st.write("Posez une question sur un établissement marocain (FR/AR/EN).")

                if "chat_history" not in st.session_state:
                    st.session_state.chat_history = []

                # Detect language
                def detect_language(text):
                    try:
                        return detect(text)
                    except:
                        return "en"

                # Identify institution
                def find_institution(text):
                        text = text.lower()
                        for name in data:
                            if name.lower() in text:
                                return name
                        return None

                # Identify requested section/topic
                def find_topic(text):
                    text = text.lower()

                    if re.search(r"\b(program|programme|programmes|specialties|specialisations|spécialité|p|برامج|تخصصات)\b", text):
                        return "Programmes"
                    elif re.search(r"\b(admission|inscription|modalité|modalites|شروط|ولوج)\b", text):
                        return "Modalites_Inscription"
                    elif re.search(r"\b(career|carrière|débou|perspectives|فرص|وظائف)\b", text):
                        return "Perspectives_Carriere"
                    elif re.search(r"\b(localisation|location|où|اين)\b", text):
                        return "Localisation"
                    elif re.search(r"\b(présentation|presentation|مقدمة|تعريف)\b", text):
                        return "Presentation"
                    else:
                        return None


                # Format each section
                def format_section(info, topic, lang):
                    if topic == "Programmes":
                        prog = info.get("Programmes")
                        if not prog:
                            return "❌ Aucune information disponible."
                        response = f"**📚 Programmes :**\n"
                        if isinstance(prog, list):
                            response += "\n".join(f"- {p}" for p in prog)
                        elif isinstance(prog, dict):
                            for cat, items in prog.items():
                                response += f"\n**{cat}**\n"
                                if isinstance(items, list):
                                    response += "\n".join(f"- {i}" for i in items) + "\n"
                                else:
                                    response += f"- {items}\n"
                        return response

                    elif topic == "Modalites_Inscription":
                        m = info.get("Modalites_Inscription", {})
                        return f"**📝 Admission :**\n- Conditions : {m.get('Conditions', 'N/A')}\n- Procédure : {m.get('Procedure', 'N/A')}"

                    elif topic == "Perspectives_Carriere":
                        careers = info.get("Perspectives_Carriere", [])
                        return "**💼 Débouchés :**\n" + "\n".join(f"- {c}" for c in careers)

                    elif topic == "Localisation":
                        return f"**📍 Localisation :** {info.get('Localisation', 'Non spécifiée')}"

                    elif topic == "Presentation":
                        return f"**📘 Présentation :**\n{info.get('Presentation', 'N/A')}"

                    else:
                        return "❓ Veuillez préciser si vous voulez les programmes, l’admission, la présentation, etc."

                # Main response generator
                def get_response(user_input, lang):
                    institution = find_institution(user_input)
                    topic = find_topic(user_input)

                    # Use last mentioned institution if not detected
                    if not institution:
                        institution = st.session_state.get("last_institution")

                    # If still missing
                    if not institution:
                        return {
                            "fr": "❓ Je n’ai pas reconnu l’établissement.",
                            "ar": "❓ لم أتمكن من تحديد المؤسسة.",
                            "en": "❓ I couldn't identify the institution."
                        }.get(lang)

                    # Remember for later messages
                    st.session_state.last_institution = institution

                    info = data[institution]

                    # ✅ If topic found, respond immediately
                    if topic:
                        return format_section(info, topic, lang)

                    # ❌ Otherwise, ask user to clarify
                    return {
                        "fr": f"❓ Vous avez mentionné **{institution}**. Souhaitez-vous connaître ses *programmes*, *admission*, *localisation* ou *débouchés* ?",
                        "ar": f"❓ لقد ذكرت **{institution}**. هل تريد معرفة *البرامج* أو *شروط القبول* أو *الموقع* أو *الآفاق*؟",
                        "en": f"❓ You mentioned **{institution}**. Would you like to know about *programs*, *admission*, *location*, or *careers*?"
                    }.get(lang)



                    # Input box
                st.chat_message("assistant").markdown("💬 Exemple : _Quelles sont les spécialités de l’ENCG ?_")

                user_input = st.chat_input("Posez votre question ici...")
                if user_input:
                    lang = detect_language(user_input)
                    response = get_response(user_input, lang)

                    st.session_state.chat_history.append(("user", user_input))
                    st.session_state.chat_history.append(("bot", response))

                # Display full chat history
                for role, msg in st.session_state.chat_history:
                    avatar = "🧑" if role == "user" else "🎓"
                    with st.chat_message(role, avatar=avatar):
                        st.markdown(msg)

                            

            else:
                # Inject custom CSS for centered title and star style
                st.markdown("""
                    <style>
                    .star-rating {
                        font-size: 2.5rem;
                        color: #d3d3d3;
                        cursor: pointer;
                    }
                    .star-rating .selected {
                        color: #ffc107;
                    }
                    .center {
                        text-align: center;
                    }
                    </style>
                """, unsafe_allow_html=True)

                # Centered title
                st.markdown("<h1 class='center'>⭐ Rate Our Service</h1>", unsafe_allow_html=True)

                # Star rating with emojis
                rating = st.radio(
                    "How would you rate us?",
                    options=[1, 2, 3, 4, 5],
                    format_func=lambda x: "⭐" * x,
                    horizontal=True
                )

                # Optional feedback
                feedback = st.text_area("Optional Feedback", placeholder="Tell us more...")

                # Submit button
                if st.button("Submit"):
                    st.success(f"Thanks for rating us {rating} star{'s' if rating > 1 else ''}! 🌟")
                    if feedback:
                        st.info(f"📝 Your feedback: {feedback}")




                        # I finish this project!!!!                        
                        # # I am so happy to finish this project, I hope you like it and find it useful
