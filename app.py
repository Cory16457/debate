import streamlit as st
import json
from cerebras.cloud.sdk import Cerebras
import fitz  
API_KEY = "cbrs api key"
client = Cerebras(api_key=API_KEY)

st.set_page_config(page_title="Debate AI", layout="wide")

st.markdown(
    "<h1 style='text-align: center;'>🎙️ Debate AI</h1><p style='text-align:center;'>Real-time AI Rebuttals, Simulations, and Judging</p>",
    unsafe_allow_html=True,
)

mode = st.sidebar.radio("Choose a Mode", ["Rebuttal", "Simulate", "Judge", "Flow Practice"])


if mode == "Rebuttal":
    st.subheader("🔁 Rebuttal Mode")
    debate_format = st.selectbox("Select Debate Format (Rebuttal)", ["Public Forum (PF)", "Lincoln-Douglas (LD)"], key="rebuttal_format")
    user_argument = st.text_area("Paste your opponent's argument:")

    if st.button("Generate Rebuttal"):
        if not user_argument.strip():
            st.warning("Please enter an argument to rebut.")
        else:
            if debate_format == "Public Forum (PF)":
                system_prompt = "You are a skilled high school Public Forum debater. Respond with clear, well-structured rebuttals using evidence and logic appropriate for PF."
            else:
                system_prompt = "You are a skilled high school Lincoln-Douglas debater. Respond with value-criterion based rebuttals using philosophical reasoning and logic."

            with st.spinner("Thinking..."):
                try:
                    response = client.chat.completions.create(
                        model="llama-4-scout-17b-16e-instruct",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_argument},
                        ]
                    )
                    rebuttal = response.choices[0].message.content
                    st.markdown("**🗣️ Rebuttal:**")
                    st.write(rebuttal)
                except Exception as e:
                    st.error(f"❌ Error: {e}")


elif mode == "Simulate":
    st.subheader("🗣️ Live Debate Mode")


    debate_format = st.selectbox("Select Debate Format (Simulate)", ["Public Forum (PF)", "Lincoln-Douglas (LD)"], key="simulate_format")
    sides = ["Pro", "Con"] if debate_format == "Public Forum (PF)" else ["Affirmative", "Negative"]
    user_side = st.radio("Which side are you arguing?", sides, key="simulate_side")
    ai_side = sides[1] if user_side == sides[0] else sides[0]


    if "debate_turns" not in st.session_state:
        st.session_state.debate_turns = []
        st.session_state.turn_count = 0
        st.session_state.messages = [
            {
                "role": "system",
                "content": f"""
You are debating as the {ai_side} side in a high school {debate_format} debate round.
Respond clearly with logical contentions and real sources. Speak only when it's your turn.
"""
            }
        ]


    if st.session_state.turn_count > 0:
        last_turn = st.session_state.debate_turns[-1]
        st.markdown(f"**🧑 {user_side}:** {last_turn['user']}")
        st.markdown(f"**🤖 {ai_side}:** {last_turn['ai']}")

    user_input = st.text_input(f"Your next {user_side} argument:")

    if st.button("Send to AI") and user_input.strip():
        with st.spinner("AI is thinking..."):
            st.session_state.messages.append({"role": "user", "content": user_input})

            try:
                response = client.chat.completions.create(
                    model="llama-4-scout-17b-16e-instruct",
                    messages=st.session_state.messages
                )
                ai_response = response.choices[0].message.content

                st.session_state.debate_turns.append({
                    "user": user_input,
                    "ai": ai_response
                })
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
                st.session_state.turn_count += 1
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")

    if st.button("🔁 Reset Debate"):
        st.session_state.debate_turns = []
        st.session_state.turn_count = 0
        st.session_state.messages = [
            {
                "role": "system",
                "content": f"""
You are debating as the {ai_side} side in a high school {debate_format} debate round.
Respond clearly with logical contentions and real sources. Speak only when it's your turn.
"""
            }
        ]
        st.rerun()

elif mode == "Judge":
    st.subheader("⚖️ Judge Mode")

    debate_format = st.selectbox("Select Debate Format (Judge)", ["Public Forum (PF)", "Lincoln-Douglas (LD)"], key="judge_format")
    sides = ["Pro", "Con"] if debate_format == "Public Forum (PF)" else ["Affirmative", "Negative"]

    side1_text = st.text_area(f"{sides[0]} Side's Argument or Transcript:")
    side2_text = st.text_area(f"{sides[1]} Side's Argument or Transcript:")

    if st.button("Judge the Debate"):
        if not side1_text.strip() or not side2_text.strip():
            st.warning("Please enter arguments for both sides.")
        else:
            with st.spinner("Deliberating..."):
                try:
                    system_prompt = f"""
You are an experienced high school {debate_format} judge. You will be given arguments or transcripts from both sides of a round.

Evaluate the quality of reasoning, evidence, clash, impact weighing, and argumentation strategy. Then:
- Declare a winner ({sides[0]} or {sides[1]})
- Provide a detailed Reason For Decision (RFD)
- Give speaker points (0–30 scale) for each side

Be fair, analytical, and specific — just like in a real tournament.
"""

                    response = client.chat.completions.create(
                        model="llama-4-scout-17b-16e-instruct",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"{sides[0]} side says:\n{side1_text.strip()}"},
                            {"role": "user", "content": f"{sides[1]} side says:\n{side2_text.strip()}"},
                        ]
                    )

                    verdict = response.choices[0].message.content
                    st.markdown("**🧑‍⚖️ Verdict:**")
                    st.write(verdict)
                except Exception as e:
                    st.error(f"❌ Error: {e}")

elif mode == "Flow Practice":
    st.subheader("⚡ Flow Practice Mode")

    debate_format = st.selectbox("Select Debate Format (Flow Practice)", ["Public Forum (PF)", "Lincoln-Douglas (LD)"], key="flow_format")

    if "practice_args" not in st.session_state:
        st.session_state.practice_args = ""

    if st.button("🎯 Generate Practice Arguments"):
        with st.spinner("Generating arguments..."):
            prompt = f"""
You are a skilled high school {debate_format} debater.

Generate 2–3 flowable arguments for a randomly selected topic in {debate_format} format.
Do **not** reuse past NSDA topics. Use creative or underused themes across economics, education, technology, law, ethics, or international relations.
Do not repeat the same resolution more than once. Be diverse.
"""

            try:
                response = client.chat.completions.create(
                    model="llama-4-scout-17b-16e-instruct",
                    messages=[
                        {"role": "system", "content": prompt}
                    ]
                )
                st.session_state.practice_args = response.choices[0].message.content
            except Exception as e:
                st.error(f"❌ Error generating arguments: {e}")

    if st.session_state.practice_args:
        st.markdown("**📋 Practice Arguments:**")
        st.code(st.session_state.practice_args)

        user_rebuttal = st.text_area("Type your response (rebuttal/collapse/weigh):")

        if st.button("🧑‍⚖️ Get AI Feedback"):
            with st.spinner("Evaluating your flow..."):
                try:
                    feedback_prompt = f"""
Here are the original debate arguments:

{st.session_state.practice_args}

Here is the user's response:

{user_rebuttal}

Give specific feedback: did they address each argument? Were the responses logical? Did they collapse or weigh effectively? Respond like a coach.
"""
                    response = client.chat.completions.create(
                        model="llama-4-scout-17b-16e-instruct",
                        messages=[
                            {"role": "system", "content": feedback_prompt}
                        ]
                    )
                    feedback = response.choices[0].message.content
                    st.markdown("**🧠 AI Feedback:**")
                    st.write(feedback)
                except Exception as e:
                    st.error(f"❌ Error getting feedback: {e}")

        if st.button("🔁 New Practice Round"):
            st.session_state.practice_args = ""
            st.rerun()
