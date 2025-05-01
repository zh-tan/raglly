import streamlit as st
from PIL import Image
import base64
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('zh.env', override=True)
url = "https://api.openai.com/v1/vector_stores/vs_681345cf76d08191aeaafd4763bf4aca/search"
api_key = os.getenv("OPENAI_API_KEY")  # or replace with your API key string
client = OpenAI()

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "query": "Summarized what sun said",
    # "filters": {
    #     "type": "eq",
    #     "key": "party",
    #     "value": "WP (Worker's Party)"
    # }
}

logo = Image.open("static/pap-logo.png")

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

pap_img = get_base64_image("static/pap-logo.png")
wp_img = get_base64_image("static/wp-logo.png")
sdp_img = get_base64_image("static/sdp-logo.png")
# alexis_img = get_base64_image("static/punggol-alexis.webp")



# Read the contents of the text file
with open("./processed/pap_2704_jalankayu_summary.txt", "r", encoding="utf-8") as file:
    pap_2704_jalankayu_summary = file.read()
# Read the contents of the text file
with open("./processed/wp_2804_punggol_summary.txt", "r", encoding="utf-8") as file:
    wp_2804_punggol_summary = file.read()

with open("./processed/pap_2604_punggol_summary.txt", "r", encoding="utf-8") as file:
    pap_2604_punggol_summary = file.read()

with open("./processed/wp_2604_tampines_summary.txt", "r", encoding="utf-8") as file:
    wp_2604_tampines_summary = file.read()

with open("./processed/sdp_2604_bukitpanjang_summary.txt", "r", encoding="utf-8") as file:
    sdp_2604_bukitpanjang_summary = file.read()

with open("./processed/pap_0105_punggol_summary.txt", "r", encoding="utf-8") as file:
    pap_0105_punggol_summary = file.read()

with open("./processed/sdp_2904_sembawang_summary.txt", "r", encoding="utf-8") as file:
    sdp_2904_bukitpanjang_summary = file.read()

with open("./processed/wp_0105_hougang_summary.txt", "r", encoding="utf-8") as file:
    wp_0105_hougang_summary = file.read()    


grc_summaries = {
    '[PAP] 01 May - Punggol': pap_0105_punggol_summary,
    '[WP] 01 May - Hougang': wp_0105_hougang_summary,
    '[SDP] 29 Apr - Bukit Panjang': sdp_2904_bukitpanjang_summary,
    '[WP] 28 Apr - Punggol': wp_2804_punggol_summary,
    '[PAP] 27 Apr - Jalan Kayu': pap_2704_jalankayu_summary,
    '[PAP] 26 Apr - Punggol': pap_2604_punggol_summary,
    '[WP] 26 Apr - Tampines': wp_2604_tampines_summary,
    '[SDP] 26 Apr - Bukit Panjang': sdp_2604_bukitpanjang_summary,
}

grc_photos = {
    '[PAP] 01 May - Punggol': get_base64_image('./static/summary-pic/pap-punggol.jpg'),
    '[WP] 01 May - Hougang': get_base64_image('./static/summary-pic/wp-hougang.jpg'),
    '[SDP] 29 Apr - Bukit Panjang': get_base64_image('./static/summary-pic/sdp-bukitpanjang.jpg'),
    '[WP] 28 Apr - Punggol': get_base64_image('./static/summary-pic/wp-punggol.png'),
    '[PAP] 27 Apr - Jalan Kayu': get_base64_image('./static/summary-pic/pap-jalankayu.jpg'),
    '[PAP] 26 Apr - Punggol': get_base64_image('./static/summary-pic/pap-punggol.jpg'),
    '[WP] 26 Apr - Tampines': get_base64_image('./static/summary-pic/wp-tampines.jpg'),
    '[SDP] 26 Apr - Bukit Panjang': get_base64_image('./static/summary-pic/sdp-bukitpanjang.jpg')
}



def build_llm_prompt(user_query):
        
    payload_q = {
    "query": user_query,
    # "filters": {
    #     "type": "eq",
    #     "key": "party",
    #     "value": "WP (Worker's Party)"
    # }
    }
    
    response = requests.post(url, headers=headers, json=payload_q)
    search_results = response.json()
    print(search_results)
    # return search_results
    context_blocks = []

    for result in search_results["data"]:
        score = result['score']
        
        # threshold
        if score < 0.75:
            continue 
            
        speaker = result["attributes"]["speaker"]
        party = result["attributes"]["party"]
        grc = result["attributes"]["grc"]
        content = result["content"][0]["text"]

        context_blocks.append(f"""
### Speaker: {speaker}
**Party:** {party}  
**GRC:** {grc}  
**Summary:**  
{content.strip()}
""")

    context_text = "\n".join(context_blocks)

    prompt = f"""
You are a helpful assistant analyzing political speeches from the Singapore General Election 2025 rallies.

The user has asked: **{user_query}**

Below are speech summaries from various candidates and guest speakers, including their party affiliation and GRC:

{context_text}

---

Please answer the user's question based on the content above. If the question is broad, synthesize and summarize the key themes and contrasts across the speeches.

**Instructions:**
- Use information only from the summaries provided above.
- Structure your response by **theme** (e.g., cost of living, housing, jobs) or by **party**, whichever fits the query better.
- Be concise, neutral, and informative.
- If a topic is not mentioned in the context, say so clearly.

Your response:
"""

    return [{"role": "user", "content": prompt}]


def user_chat(prompt):
    messages = build_llm_prompt(prompt)
    chat_response = client.chat.completions.create(
    model="gpt-4.1-mini",
    messages=messages,
    temperature=0.3
)   
    return chat_response.choices[0].message.content



# --- Streamlit App UI ---
st.set_page_config(page_title="Ra(g)lly: Chat with Rally Speeches", layout="wide")
st.title("Ra(g)lly - Chat with 🔥 rally highlights!!")
st.markdown("Look left, Look right, so many rallies where got time see all?")

tabs = st.tabs(["Rally Info & Chat", "2025 Election Map"])

with tabs[0]:
    # st.header("Rally Summaries & Chat")
    rally_list = list(grc_summaries.keys())
    selected_rally = st.selectbox("Select a Rally:", rally_list, key="rally_select")
    st.markdown("---")
    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.subheader("Rally Summary")
        st.image(f"data:image/png;base64,{grc_photos[selected_rally]}")
        
        # PARTY PHOTOS 
        #party_logo_html = f'''<div style="display: flex; align-items: center;"><img src="data:image/png;base64,{alexis_img}" width="40" style="margin-right: 12px;"><b>PAP</b></div>'''
        #st.markdown(party_logo_html, unsafe_allow_html=True)
        
        # Determine party for logo display based on key
        party_logo_html = ""
        if selected_rally.lower().startswith('[pap'):
            party_logo_html = f'''<div style="display: flex; align-items: center;"><img src="data:image/png;base64,{pap_img}" width="40" style="margin-right: 12px;"><b>PAP</b></div>'''
        elif selected_rally.lower().startswith('[wp'):
            party_logo_html = f'''<div style="display: flex; align-items: center;"><img src="data:image/png;base64,{wp_img}" width="40" style="margin-right: 12px;"><b>WP</b></div>'''
        if party_logo_html:
            st.markdown(party_logo_html, unsafe_allow_html=True)
        st.write(grc_summaries[selected_rally])
    with col2:
        st.subheader("Find out more about Rally/ Manifesto!")
        button_questions = [
            "Summarize what Lawrence Wong said and promised.",
            "Can you compare between WP and PAP in Punggol? List down the promises.",
            "What did WP mention about potential issues faced by Singaporeans?",
            "Summarize what Pritam Singh said during the rally."
        ]
        chat_key = f"chat_history_{selected_rally}_combined"
        if chat_key not in st.session_state:
            st.session_state[chat_key] = []
        selected_btn = None
        for i, q in enumerate(button_questions):
            if st.button(q, key=f"btn_{selected_rally}_{i}"):
                selected_btn = q
        user_input = st.text_input(f"Ask something about this rally:", key=f"input_{selected_rally}_combined")
        if selected_btn and (not user_input or user_input.strip() == ""):
            user_input = selected_btn
        if user_input:
            response = user_chat(user_input + "\n\nContext: user currently selected" + selected_rally)
            # Insert the new chat at the top
            st.session_state[chat_key].insert(0, (user_input, response))
        for q, a in st.session_state[chat_key]:
            st.markdown(f"**You:** {q}")
            st.markdown(f"**ra(g)lly:** {a}")

with tabs[1]:
    st.header("2025 Singapore Election Map")
    st.markdown(
        '''
        <iframe
          id="responsive-iframe"
          src="https://elections.data.gov.sg/en/map?isScrollable=true&primaryColor=%236253E8&view=Winning%20margin&lang=en&year=2025&constituenciesView=all"
          frameborder="0"
          scrolling="no"
          width="100%"
          height="642px"
        >
        </iframe>
        <script>
          function adjustIframeHeight() {
            const iframe = document.getElementById('responsive-iframe');
            const width = iframe.offsetWidth;
            if (width < 768) {
              iframe.style.height = '1040px';
            } else {
              iframe.style.height = '642px';
            }
          }
          window.addEventListener('load', adjustIframeHeight);
          window.addEventListener('resize', adjustIframeHeight);
        </script>
        ''', unsafe_allow_html=True
    )
