import streamlit as st # type: ignore

# Setting Streamlit page config
st.set_page_config(page_title="ResuMate",layout="wide")

#🤖 ResuMate — An Conversational JD Analysis Using LLM's for Resume Shortlisting
# # ------------- HEADER ----------------
# st.markdown("""
#     <h2 style='text-align: center; color: #EB0525;'>🤖 Screening Agent for HR Teams
# </h2>
#     <hr style='margin-top: 0;'>
# """, unsafe_allow_html=True)
# # ------------- END ----------------

import PyPDF2 as pdf    # type: ignore
import pandas as pd     # type: ignore
import re
import json

from dotenv import load_dotenv
import os
import PyPDF2 as pdf                # type: ignore
from langchain_groq import ChatGroq # type: ignore

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
print(api_key)


## -------------------------------------- Cleaning LLM RAW Output -----------------------------------
def cleaning_llm_text(text):
    """Extract the first JSON object from a messy string."""
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        return match.group(0)
    else:
        raise ValueError("No valid JSON block found in text")
# ---------------------------------------------------------------------------------------------------

# -------------------------------Text from PDF--------------------------------------------------
#returning text from pdf
def input_pdf_text(uploaded_file):
    reader=pdf.PdfReader(uploaded_file)
    text=""
    for page in range(len(reader.pages)):
        page=reader.pages[page]
        text+=str(page.extract_text())
    return text
# ----------------------------------------------------------------------------------------------

# -------------------------------Dialog Function----------------------------------------------------
@st.dialog("🧠 Reason for Evaluation")
def show_reason_dialog(i, filename, reason):
    st.markdown(f"### 📄 {filename}")
    st.markdown("**Explanation by LLM:**")
    st.write(reason)
# ----------------------------------------------------------------------------------------------


# --------------------------------Coloring %----------------------------------------------
def color_match(val):
    if val == "N/A":
        return f'<span style="color: gray; font-style: italic;">N/A</span>'
    
    try:
        percent = int(val.strip('%'))
    except:
        return 'Result was N/A'
    
    if percent >= 60:
        return f'<span style="color: green; font-weight: bold;">{val}</span>'
    elif percent >= 40:
        return f'<span style="color: orange; font-weight: bold;">{val}</span>'
    else:
        return f'<span style="color: red; font-weight: bold;">{val}</span>'
# -------------------------------------------------------------------------------------------


def frontab_function():
    st.title("Hiring Simplified")

    input_prompt="""
    ### RESUME TEXT:
    {text}
    ### Job Description:
    {jd}
    ### INSTRUCTION:
    Hey Act Like a skilled or very experienced ATS(Application Tracking System)
    with a deep understanding of tech field,software engineering,data science ,data analyst
    and big data engineer. Your task is to evaluate the resume based on the given job description.
    You must consider the job market is very competitive.

    Assign the percentage Matching based on Jd and the missing keywords with high accuracy.
    Give profile summary as brief as possible(in less than a line).
    Also, provide a brief reason for your scoring — this will be shown to the candidate as feedback.

    If the resume had different job profile than the one mentioned in Job Description, reduce the percentage more.
    
    ### OUTPUT FORMAT (valid JSON only):
    {{
        "JD Match": "XX%",
        "Missing Keywords": [],
        "Profile Summary": "",
        "Details": ""
    }}
    ### VALID JSON (NO PREAMBLE):
    """

    jd=st.text_area("Paste the Job Description")
    uploaded_files=st.file_uploader("Upload Your Resume",type="pdf",help="Please upload the pdf",accept_multiple_files=True)

    submit = st.button("RUN 🤖")

    # Step 1: Initialize df in session_state if not already
    if "df" not in st.session_state:
        st.session_state.df = None

    placeholder = st.empty()

    if submit and uploaded_files and jd:
        ## -------------------------------------- Setting Up LLM Model --------------------------------------
        llm = ChatGroq(
            temperature=0,
            groq_api_key=api_key,
            model=st.session_state.get("groq_model", "llama-3.3-70b-versatile")
        )
        st.text('writing Api key')
        
        def get_llm_response(prompt):
            st.info('Getting Response from Groq ....')
            return llm.invoke(prompt).content
        
        
        # Printing what model we have used
        # st.success(f"✅ Using {st.session_state['llm_engine']} model: " +
        #    f"{st.session_state.get('groq_model') if st.session_state['llm_engine'] == 'Groq' else st.session_state.get('ollama_model')}")
        ##---------------------------------------------------------------------------------------------------
            

        with st.spinner("🔍 Creating Table..."):
            # -------------- UI --------------
            placeholder.progress(0)
            # -------------- END -------------

            results=[]
            #extracting text from pdf 1 by 1
            for i,uploaded_file in enumerate(uploaded_files):
                #----------- UI -----------
                st.caption(f'Analyzing {uploaded_file.name} 👁️‍🗨️👁️‍🗨️')
                #--------------------------

                text=input_pdf_text(uploaded_file)
                #Prompt formatting
                formatted_prompt = input_prompt.format(text=text, jd=jd)
                #extracting response
                # response=get_llm_response(formatted_prompt)
                try:
                    raw_response = get_llm_response(formatted_prompt)

                    # Converting Raw String Response from LLM to Json
                    json_parser = JsonOutputParser()
                    clean_response = cleaning_llm_text(raw_response)

                    parsed = json_parser.parse(clean_response)

                    # -------------- UI --------------
                    st.json(parsed)
                    st.success(f"✅ {uploaded_file.name} Data extracted!")
                    # -------------- END -------------

                    jd_match = parsed.get("JD Match", "N/A")
                    missing_keywords = parsed.get("Missing Keywords", "N/A")
                    profile_summary = parsed.get("Profile Summary", "N/A")
                    details_reason = parsed.get("Details", "N/A")

                except Exception as e:
                    st.error(f"❌ Failed to parse response from LLM for {uploaded_file.name}")
                    st.error(f"ERROR : {e}")
                    st.warning(f"Raw Rsponse \n: {raw_response}", icon="⚠️")
                    jd_match = "N/A"
                    missing_keywords = "N/A"
                    profile_summary = "N/A"
                    details_reason = "N/A"
    

                # -------------- UI --------------
                placeholder.progress(50)
                # -------------- END -------------

                results.append({
                    "File Name": uploaded_file.name,
                    "JD Match %": jd_match,
                    "Missing Keywords": missing_keywords,
                    "Profile Summary": profile_summary,
                    "Details": details_reason  # Don't show this in the main markdown table
                    # Storing full response for explanation
                })
            
            # -------------- UI --------------
            placeholder.progress(75)
            #placeholder.progress(int(((i + 1) / len(uploaded_files)) * 75))
            # -------------- END -------------

            # Convert to Pandas DATAFRAME
            df = pd.DataFrame(results)


            # --------------------------------- VIEW BUTTON ---------------------------------
            # Store row-level reason strings
            st.session_state.details_map = {}

            # Create "View" buttons and store associated reasoning
            details_buttons = []
            for i, row in df.iterrows():
                st.session_state.details_map[f"details_{i}"] = row["Details"]
                # details_buttons.append(f'<button id="details_{i}" class="view-btn">👁️ View</button>')
                details_buttons.append(f'👁️ View')

            df["Details"] = details_buttons


            # -------------- TABLE UI --------------
            st.subheader("📜 Resume Analysis")

            #Apply colors to JD Match column
            try:
                df["JD Match %"] = df["JD Match %"].apply(lambda x: color_match(x))     
            except:
                print("Coloring Error")
            # -------------- END -------------------
            

            #----------------------------------------
            st.session_state.df = df
            #----------------------------------------
            

            # -------------- UI --------------
            placeholder.progress(100)
            # -------------- END -------------
            

    #--------------------------------------------------------------------------------
    # Step 3: Display checkbox and dataframe ONLY if df exists
    if st.session_state.df is not None:
        
        #--------------------------- Filter Rows by JD Match % (Slider) -----------------------
        min_score = st.slider("📊 Minimum JD Match %", min_value=0, max_value=100, value=0)

        # Prepare filtered DataFrame
        def strip_percent(val):
            import re
            return int(re.sub(r"%", "", re.sub(r"<.*?>", "", val))) if isinstance(val, str) else 0

        df_filtered = st.session_state.df.copy()
        df_filtered["score_filter"] = df_filtered["JD Match %"].apply(strip_percent)
        df_filtered = df_filtered[df_filtered["score_filter"] >= min_score]
        df_filtered.drop(columns=["score_filter"], inplace=True)

        # Table Sorting in Descending(TOP ROW --- Candidate with Highest JD %)
        df_filtered["score_sort"] = df_filtered["JD Match %"].apply(strip_percent)
        df_filtered = df_filtered.sort_values(by="score_sort", ascending=False).drop(columns=["score_sort"])


        # Show only Filtered Table
        # st.dataframe(df_filtered.drop(columns=["Details"]), use_container_width=st.checkbox("Use container width?"))
        st.markdown(df_filtered.drop(columns=["Details"]).to_html(escape=False, index=False), unsafe_allow_html=True)

        #-------------------------------------------------------------------------------



        # --------------------------------- Downlaod CSV ---------------------------------
        # Prepare a raw, clean version for export
        df_export = df_filtered.copy()

        # Strip HTML tags from JD Match column if needed
        import re
        def clean_html(val):
            return re.sub(r"<.*?>", "", val) if isinstance(val, str) else val
        
        df_export["JD Match %"] = df_export["JD Match %"].apply(clean_html)

        # Remove the View button column and insert back real details (optional)
        df_export["Details"] = [
            st.session_state.details_map[f"details_{i}"] 
            for i in df_export.index
            ]
        
        import time

        # Add download button
        if st.download_button(
            label="📥 Download Filtered Table as CSV",
            data=df_export.to_csv(index=False),
            file_name="resume_analysis.csv",
            mime="text/csv"
        ):
            time.sleep(.5)
            st.toast('CSV Downloaded!', icon='🎉')
        
        #-------------------------------------------------------------------------------

        st.divider()

        # --------------------------------- Dialog Logic ---------------------------------
        # Handle View Button Logic
        # Show Dialog on View click
        for i in range(len(st.session_state.df)):
            filename = st.session_state.df.iloc[i]["File Name"]
            reason = st.session_state.details_map[f"details_{i}"]

            if st.button(f"📄 {filename} : Details", key=f"view_{i}"):
                show_reason_dialog(i, filename, reason)
        # -------------------------------------------------------------------------------
    
    
    placeholder.empty()

    # st.divider()


frontab_function()


# ------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; color: grey;'>
        © 2025 Ansh
    </div>
    """,
    unsafe_allow_html=True
)
# ------------- END ----------------