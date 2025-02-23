import streamlit as st
from dotenv import load_dotenv
import json
from datetime import datetime
import re

# Load environment variables
load_dotenv()

def init_session_state():
    """Initialize session state variables."""
    if 'project_stage' not in st.session_state:
        st.session_state.project_stage = 'initial'
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'analysis_timestamp' not in st.session_state:
        st.session_state.analysis_timestamp = None

def extract_section(text, section_marker):
    """Extract a section from the analysis text."""
    pattern = f"{section_marker}:(.*?)(?=\\n\\n|$)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1).strip() if match else None

def extract_json_summary(text):
    """Extract the JSON summary from the text."""
    try:
        # Find the last occurrence of a JSON-like structure
        json_pattern = r'{\s*"key_assumptions":.+}'
        match = list(re.finditer(json_pattern, text, re.DOTALL))[-1]
        json_str = match.group(0)
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Failed to parse JSON summary: {str(e)}")
        return None

def display_analysis_results(result):
    """Display the analysis results in a structured and user-friendly way."""
    st.write("### Initial Analysis Results")
    st.write(f"Analysis completed at: {st.session_state.analysis_timestamp}")
    
    raw_text = result.raw
    
    # Display initial thoughts
    initial_thoughts = extract_section(raw_text, "INITIAL THOUGHTS")
    if initial_thoughts:
        st.write("#### 💭 Initial Analysis")
        st.write(initial_thoughts)
    
    # Extract and display assumptions
    assumptions_pattern = r"ASSUMPTION:(.*?)REASONING:(.*?)(?=ASSUMPTION:|RISK:|$)"
    assumptions = re.finditer(assumptions_pattern, raw_text, re.DOTALL)
    if assumptions:
        st.write("#### 🎯 Key Assumptions to Validate")
        for match in assumptions:
            assumption = match.group(1).strip()
            reasoning = match.group(2).strip()
            with st.expander(f"**{assumption}**"):
                st.write("**Reasoning:**", reasoning)
    
    # Extract and display risks
    risks_pattern = r"RISK:(.*?)POTENTIAL IMPACT:(.*?)(?=RISK:|NEXT STEPS:|$)"
    risks = re.finditer(risks_pattern, raw_text, re.DOTALL)
    if risks:
        st.write("#### ⚠️ Risks and Challenges")
        for match in risks:
            risk = match.group(1).strip()
            impact = match.group(2).strip()
            with st.expander(f"**{risk}**"):
                st.write("**Potential Impact:**", impact)
    
    # Extract and display next steps
    next_steps_section = extract_section(raw_text, "NEXT STEPS")
    if next_steps_section:
        st.write("#### 👣 Recommended Next Steps")
        steps = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', next_steps_section, re.DOTALL)
        for i, step in enumerate(steps, 1):
            st.write(f"{i}. {step.strip()}")
    
    # Extract and display validations
    validations_pattern = r"VALIDATION NEEDED:(.*?)METHOD:(.*?)(?=VALIDATION NEEDED:|BMC ELEMENT|$)"
    validations = re.finditer(validations_pattern, raw_text, re.DOTALL)
    if validations:
        st.write("#### 🔍 Required Validations")
        for match in validations:
            validation = match.group(1).strip()
            method = match.group(2).strip()
            with st.expander(f"**{validation}**"):
                st.write("**Suggested Method:**", method)
    
    # Extract and display BMC elements
    bmc_pattern = r"BMC ELEMENT - (.*?):(.*?)(?=BMC ELEMENT|{|$)"
    bmc_elements = re.finditer(bmc_pattern, raw_text, re.DOTALL)
    if bmc_elements:
        st.write("#### 📊 Initial Business Model Canvas Elements")
        bmc_cols = st.columns(2)
        for i, match in enumerate(bmc_elements):
            element = match.group(1).strip()
            description = match.group(2).strip()
            with bmc_cols[i % 2]:
                with st.expander(f"**{element}**"):
                    st.write(description)

def main():
    st.set_page_config(
        page_title="Lean Startup AI Advisor",
        page_icon="🚀",
        layout="wide"
    )

    init_session_state()

    st.title("Lean Startup AI Advisor 🚀")
    st.subheader("Your AI-powered startup methodology guide")

    # Initial idea input section
    with st.form(key='startup_form'):
        idea_type = st.selectbox(
            "What would you like to start with?",
            ["Initial Idea", "Customer Segment", "Pain Point"],
            key='idea_type'
        )
        
        idea_description = st.text_area(
            f"Describe your {idea_type.lower()}:",
            height=150,
            key='idea_description'
        )
        
        submit_button = st.form_submit_button("Start Analysis")

    if submit_button and idea_description:
        st.session_state.analysis_running = True
        st.session_state.project_stage = 'analysis'
        st.session_state.analysis_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display processing status
        with st.spinner("🤖 AI agents are analyzing your input..."):
            from agents.orchestrator import OrchestratorAgent
            
            # Create progress placeholder
            progress_placeholder = st.empty()
            progress_placeholder.write("🔄 Initializing analysis...")
            
            # Initialize the orchestrator agent
            orchestrator = OrchestratorAgent()
            
            progress_placeholder.write("🤖 Creating analysis tasks...")
            # Create initial tasks based on user input
            tasks = orchestrator.create_initial_tasks(
                idea_type=idea_type,
                description=idea_description
            )
            
            progress_placeholder.write("📊 Analyzing your input...")
            # Create and run the crew
            crew = orchestrator.get_crew(tasks)
            
            # Execute the crew and get results
            result = crew.kickoff()
            
            progress_placeholder.empty()
            
            # Store results in session state
            st.session_state.current_results = result

        # Display the results
        if st.session_state.current_results:
            display_analysis_results(st.session_state.current_results)
            
            # Add action buttons for next steps
            st.write("### 🚀 Next Actions")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Start Customer Interviews"):
                    st.session_state.project_stage = 'customer_interviews'
            with col2:
                if st.button("Design MVP"):
                    st.session_state.project_stage = 'mvp_design'
            with col3:
                if st.button("Review Business Model"):
                    st.session_state.project_stage = 'bmc_review'

if __name__ == "__main__":
    main()