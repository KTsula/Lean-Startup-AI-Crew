import streamlit as st
from dotenv import load_dotenv
import json
from datetime import datetime
import re
import os

# Import UI components
from ui.bmc_visualization import display_bmc, extract_bmc_from_json, interactive_bmc_editor
from ui.validation_interface import display_validation_plan, human_validation_form, generate_recommendations

import sys
import platform

# SQLite3 compatibility check
def check_sqlite_version():
    import sqlite3
    print(f"SQLite3 version: {sqlite3.sqlite_version}")
    if tuple(map(int, sqlite3.sqlite_version.split('.'))) < (3, 35, 0):
        try:
            import pysqlite3
            sys.modules['sqlite3'] = pysqlite3
            print("Replaced system SQLite3 with pysqlite3")
        except ImportError:
            print("Could not replace SQLite3. Some features may not work.")

# Run version check
check_sqlite_version()
def init_session_state():
    """Initialize session state variables."""
    if 'project_stage' not in st.session_state:
        st.session_state.project_stage = 'api_setup' if not is_api_configured() else 'initial'
    if 'analysis_running' not in st.session_state:
        st.session_state.analysis_running = False
    if 'current_results' not in st.session_state:
        st.session_state.current_results = None
    if 'analysis_timestamp' not in st.session_state:
        st.session_state.analysis_timestamp = None
    if 'bmc_data' not in st.session_state:
        st.session_state.bmc_data = None
    if 'key_assumptions' not in st.session_state:
        st.session_state.key_assumptions = []
    if 'validations' not in st.session_state:
        st.session_state.validations = []
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'market_research' not in st.session_state:
        st.session_state.market_research = None
    if 'mvp_design' not in st.session_state:
        st.session_state.mvp_design = None
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""
    if 'serper_api_key' not in st.session_state:
        st.session_state.serper_api_key = ""

def is_api_configured():
    """Check if API keys are configured in session state."""
    return (st.session_state.get("openai_api_key") and 
            st.session_state.get("serper_api_key"))

def display_api_setup():
    """Display the API setup screen for first-time users."""
    st.title("Welcome to Lean Startup AI Advisor 🚀")
    st.write("To get started, we need your API keys. These are kept in your browser's session and not stored on our servers.")
    
    with st.form("api_setup_form"):
        st.subheader("API Keys Configuration")
        
        # OpenAI API Key
        st.write("##### OpenAI API Key")
        st.write("This is used for the AI functionality. You can get one from [OpenAI's website](https://platform.openai.com/api-keys).")
        openai_key = st.text_input("Enter your OpenAI API key", type="password", 
                                 value=st.session_state.get("openai_api_key", ""))
        
        # SerperDev API Key
        st.write("##### Serper API Key")
        st.write("This is used for web searches. You can get one from [Serper.dev](https://serper.dev/).")
        serper_key = st.text_input("Enter your Serper API key", type="password", 
                                 value=st.session_state.get("serper_api_key", ""))
        
        submit_button = st.form_submit_button("Save and Continue")
        
        if submit_button:
            # Validate API keys (basic validation)
            if not openai_key or len(openai_key) < 10:
                st.error("Please enter a valid OpenAI API key")
                return
                
            if not serper_key or len(serper_key) < 10:
                st.error("Please enter a valid Serper API key")
                return
                
            # Store API keys in session state
            st.session_state.openai_api_key = openai_key
            st.session_state.serper_api_key = serper_key
            
            # Set environment variables for the current session
            os.environ["OPENAI_API_KEY"] = openai_key
            os.environ["SERPER_API_KEY"] = serper_key
            
            # Change stage to initial
            st.session_state.project_stage = 'initial'
            st.success("API keys saved successfully! You can now start using the application.")
            st.rerun()

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
        validation_list = []
        for match in validations:
            validation = match.group(1).strip()
            method = match.group(2).strip()
            with st.expander(f"**{validation}**"):
                st.write("**Suggested Method:**", method)
            validation_list.append({"validation": validation, "method": method})
        
        # Store validations in session state for later use
        st.session_state.validations = validation_list
    
    # Extract and display BMC elements
    bmc_pattern = r"BMC ELEMENT - (.*?):(.*?)(?=BMC ELEMENT|{|$)"
    bmc_elements = re.finditer(bmc_pattern, raw_text, re.DOTALL)
    if bmc_elements:
        st.write("#### 📊 Initial Business Model Canvas Elements")
        bmc_data = {}
        for match in bmc_elements:
            element = match.group(1).strip().lower().replace(" ", "_")
            description = match.group(2).strip()
            bmc_data[element] = description
        
        # Store BMC data in session state
        st.session_state.bmc_data = bmc_data
        
        # Display BMC visualization
        display_bmc(bmc_data)
    
    # Try to extract JSON summary for structured data
    try:
        json_data = extract_json_summary(raw_text)
        if json_data and "key_assumptions" in json_data:
            st.session_state.key_assumptions = json_data["key_assumptions"]
    except:
        pass

def display_customer_interviews():
    """Display the customer interviews interface."""
    st.write("# Customer Interviews")
    st.write("This section helps you validate your startup hypotheses through customer interviews.")
    
    # Display validation plan
    if st.session_state.validations:
        display_validation_plan(st.session_state.validations)
        
        # Human validation form
        results = human_validation_form(st.session_state.validations)
        if results:
            st.session_state.validation_results = results
            st.success("Validation results submitted successfully!")
            
            # Generate recommendations
            recommendations = generate_recommendations(results.get("validation_results", []))
            
            st.write("## Recommendations Based on Your Validation")
            for recommendation in recommendations:
                st.write(recommendation)

def display_mvp_design():
    """Display the MVP design interface."""
    st.write("# Minimum Viable Product (MVP) Design")
    st.write("Design your MVP based on validated assumptions and user feedback.")
    
    # Show validated assumptions if available
    if st.session_state.validation_results:
        st.write("## Validated Assumptions")
        validated = [r for r in st.session_state.validation_results.get("validation_results", []) 
                    if r.get("result") == "Validated"]
        
        for v in validated:
            st.write(f"✅ {v.get('validation_item')}")
    
    # MVP design form
    with st.form("mvp_form"):
        st.write("## Define Your MVP")
        
        mvp_name = st.text_input("MVP Name")
        
        mvp_description = st.text_area("Description", 
            help="Describe your MVP in a few sentences")
        
        core_features = st.text_area("Core Features", 
            help="List the essential features that address the key user problems")
        
        success_metrics = st.text_area("Success Metrics", 
            help="What metrics will you track to measure success?")
        
        timeline = st.text_input("Timeline", 
            help="Estimated time to develop your MVP")
        
        resources = st.text_area("Required Resources", 
            help="What resources (people, technology, funding) do you need?")
        
        submit_button = st.form_submit_button("Save MVP Design")
        
        if submit_button:
            st.session_state.mvp_design = {
                "name": mvp_name,
                "description": mvp_description,
                "core_features": core_features,
                "success_metrics": success_metrics,
                "timeline": timeline,
                "resources": resources,
                "timestamp": datetime.now().isoformat()
            }
            st.success("MVP design saved successfully!")

def display_bmc_review():
    """Display the Business Model Canvas review interface."""
    st.write("# Business Model Canvas Review")
    
    if st.session_state.bmc_data:
        # Allow user to edit the existing BMC
        st.session_state.bmc_data = interactive_bmc_editor(st.session_state.bmc_data)
    else:
        st.error("No Business Model Canvas data available. Please complete the initial analysis first.")

def display_market_research_results(research_data):
    """Display market research results in a structured and visual format."""
    st.write("## Market Research Results")
    
    # Extract sections
    market_size = extract_section(research_data, "MARKET SIZE AND TRENDS")
    if market_size:
        st.write("### 📈 Market Size and Trends")
        st.write(market_size)
    
    # Extract competitor analysis
    competitors_pattern = r"COMPETITOR:(.*?)DESCRIPTION:(.*?)STRENGTHS:(.*?)WEAKNESSES:(.*?)BUSINESS MODEL:(.*?)MARKET SHARE:(.*?)TARGET AUDIENCE:(.*?)SOURCE:(.*?)(?=COMPETITOR:|CUSTOMER INSIGHTS:|$)"
    competitors = list(re.finditer(competitors_pattern, research_data, re.DOTALL))
    
    if competitors:
        st.write("### 🏢 Competitor Analysis")
        
        # Create tabs for each competitor
        competitor_names = [match.group(1).strip() for match in competitors]
        comp_tabs = st.tabs(competitor_names)
        
        for i, (match, tab) in enumerate(zip(competitors, comp_tabs)):
            with tab:
                name = match.group(1).strip()
                description = match.group(2).strip()
                strengths = match.group(3).strip()
                weaknesses = match.group(4).strip()
                business_model = match.group(5).strip() if len(match.groups()) > 4 else "Not specified"
                market_share = match.group(6).strip() if len(match.groups()) > 5 else "Not specified" 
                target_audience = match.group(7).strip() if len(match.groups()) > 6 else "Not specified"
                source = match.group(8).strip() if len(match.groups()) > 7 else "Not specified"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Company Profile")
                    st.write("**Description:**", description)
                    st.write("**Business Model:**", business_model)
                    st.write("**Market Share:**", market_share)
                    st.write("**Target Audience:**", target_audience)
                    
                with col2:
                    st.markdown("#### SWOT Analysis")
                    st.write("**Strengths:**")
                    for strength in strengths.split('-'):
                        if strength.strip():
                            st.write(f"✅ {strength.strip()}")
                    
                    st.write("**Weaknesses:**")
                    for weakness in weaknesses.split('-'):
                        if weakness.strip():
                            st.write(f"⚠️ {weakness.strip()}")
                
                st.write("**Source:**", source)
                
                # Add a button to save competitor to evidence
                if st.button(f"Save {name} Analysis to Evidence", key=f"save_comp_{i}"):
                    from tools.evidence_tracker import EvidenceTracker
                    if 'evidence_tracker' not in st.session_state:
                        st.session_state.evidence_tracker = EvidenceTracker(storage_path='data/evidence.json')
                    
                    competitor_info = f"""
                    Competitor: {name}
                    Description: {description}
                    Strengths: {strengths}
                    Weaknesses: {weaknesses}
                    Business Model: {business_model}
                    Market Share: {market_share}
                    Target Audience: {target_audience}
                    Source: {source}
                    """
                    
                    st.session_state.evidence_tracker.add_evidence(
                        decision_id=f"competitor_{name.lower().replace(' ', '_')}",
                        evidence_type="competitor_analysis",
                        source=source,
                        content=competitor_info,
                        agent_name="Market Research Specialist",
                        confidence=4
                    )
                    
                    st.success(f"Saved {name} analysis to evidence!")
    
    # Extract customer insights
    insights_pattern = r"PAIN POINT:(.*?)EVIDENCE:(.*?)CUSTOMER QUOTE:(.*?)SOURCE:(.*?)(?=PAIN POINT:|PRICING MODELS:|$)"
    insights = list(re.finditer(insights_pattern, research_data, re.DOTALL))
    
    if insights:
        st.write("### 👥 Customer Insights")
        
        for i, match in enumerate(insights):
            pain_point = match.group(1).strip()
            evidence = match.group(2).strip()
            quote = match.group(3).strip()
            source = match.group(4).strip() if len(match.groups()) > 3 else "Not specified"
            
            with st.expander(f"Pain Point: {pain_point}"):
                st.write("**Evidence:**", evidence)
                st.write("**Customer Quote:**", f'"{quote}"')
                st.write("**Source:**", source)
                
                # Add a button to save insight to evidence
                if st.button(f"Save This Insight to Evidence", key=f"save_insight_{i}"):
                    from tools.evidence_tracker import EvidenceTracker
                    if 'evidence_tracker' not in st.session_state:
                        st.session_state.evidence_tracker = EvidenceTracker(storage_path='data/evidence.json')
                    
                    insight_info = f"""
                    Pain Point: {pain_point}
                    Evidence: {evidence}
                    Customer Quote: "{quote}"
                    Source: {source}
                    """
                    
                    st.session_state.evidence_tracker.add_evidence(
                        decision_id=f"insight_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        evidence_type="customer_insight",
                        source=source,
                        content=insight_info,
                        agent_name="Market Research Specialist",
                        confidence=4
                    )
                    
                    st.success(f"Saved customer insight to evidence!")
    
    # Extract pricing models
    pricing_pattern = r"MODEL TYPE:(.*?)PRICE RANGE:(.*?)VALUE METRICS:(.*?)COMPETITOR EXAMPLES:(.*?)SOURCE:(.*?)(?=MODEL TYPE:|REGULATORY FACTORS:|$)"
    pricing_models = list(re.finditer(pricing_pattern, research_data, re.DOTALL))
    
    if pricing_models:
        st.write("### 💰 Pricing Models")
        
        # Create a DataFrame for pricing models
        pricing_data = []
        for match in pricing_models:
            model_type = match.group(1).strip()
            price_range = match.group(2).strip()
            value_metrics = match.group(3).strip()
            examples = match.group(4).strip()
            source = match.group(5).strip() if len(match.groups()) > 4 else "Not specified"
            
            pricing_data.append({
                "Model Type": model_type,
                "Price Range": price_range,
                "Value Metrics": value_metrics,
                "Examples": examples,
                "Source": source
            })
        
        if pricing_data:
            import pandas as pd
            df = pd.DataFrame(pricing_data)
            st.dataframe(df)
    
    # Extract regulatory factors
    regulatory = extract_section(research_data, "REGULATORY FACTORS")
    if regulatory:
        st.write("### ⚖️ Regulatory Factors")
        st.write(regulatory)
    
    # Extract market trends
    trends_pattern = r"TREND:(.*?)EVIDENCE:(.*?)IMPACT ON BUSINESS:(.*?)SOURCE:(.*?)(?=TREND:|ASSUMPTION VALIDATION:|$)"
    trends = list(re.finditer(trends_pattern, research_data, re.DOTALL))
    
    if trends:
        st.write("### 🔮 Market Trends")
        
        for i, match in enumerate(trends):
            trend = match.group(1).strip()
            evidence = match.group(2).strip()
            impact = match.group(3).strip()
            source = match.group(4).strip() if len(match.groups()) > 3 else "Not specified"
            
            with st.expander(f"Trend: {trend}"):
                st.write("**Evidence:**", evidence)
                st.write("**Impact on Business:**", impact)
                st.write("**Source:**", source)
    
    # Extract assumption validations
    validation_pattern = r"ASSUMPTION:(.*?)EVIDENCE:(.*?)CONCLUSION:(.*?)CONFIDENCE:(.*?)SOURCES:(.*?)(?=ASSUMPTION:|RECOMMENDATIONS:|$)"
    validations = list(re.finditer(validation_pattern, research_data, re.DOTALL))
    
    if validations:
        st.write("### 🧪 Assumption Validation")
        
        for match in validations:
            assumption = match.group(1).strip()
            evidence = match.group(2).strip()
            conclusion = match.group(3).strip()
            confidence = match.group(4).strip()
            sources = match.group(5).strip()
            
            conclusion_icon = "✅" if "validated" in conclusion.lower() else "❌" if "invalidated" in conclusion.lower() else "⚠️"
            
            with st.expander(f"{conclusion_icon} **{assumption}**"):
                st.write("**Evidence:**", evidence)
                st.write("**Conclusion:**", conclusion)
                st.write("**Confidence:**", confidence)
                st.write("**Sources:**", sources)
    
    # Extract recommendations
    recommendations = extract_section(research_data, "RECOMMENDATIONS")
    if recommendations:
        st.write("### 🚀 Recommendations")
        
        # Try to extract numbered recommendations
        rec_list = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', recommendations, re.DOTALL)
        
        if rec_list:
            for i, rec in enumerate(rec_list, 1):
                st.write(f"{i}. {rec.strip()}")
        else:
            st.write(recommendations)

def display_customer_segment_results(research_data):
    """Display customer segment research results."""
    st.write("## Customer Segment Analysis Results")
    
    # Extract segment profile
    segment_profile = extract_section(research_data, "SEGMENT PROFILE")
    if segment_profile:
        st.write("### 👤 Customer Segment Profile")
        
        # Try to extract specific parts
        demographics = re.search(r'DEMOGRAPHICS:(.*?)(?=PSYCHOGRAPHICS:|$)', segment_profile, re.DOTALL)
        psychographics = re.search(r'PSYCHOGRAPHICS:(.*?)(?=MARKET SIZE:|$)', segment_profile, re.DOTALL)
        market_size = re.search(r'MARKET SIZE:(.*?)(?=GROWTH TRENDS:|$)', segment_profile, re.DOTALL)
        growth_trends = re.search(r'GROWTH TRENDS:(.*?)(?=SOURCE:|$)', segment_profile, re.DOTALL)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Demographics:**")
            st.write(demographics.group(1).strip() if demographics else "Not specified")
            
            st.write("**Market Size:**")
            st.write(market_size.group(1).strip() if market_size else "Not specified")
        
        with col2:
            st.write("**Psychographics:**")
            st.write(psychographics.group(1).strip() if psychographics else "Not specified")
            
            st.write("**Growth Trends:**")
            st.write(growth_trends.group(1).strip() if growth_trends else "Not specified")
    
    # Extract customer channels
    channels = extract_section(research_data, "CUSTOMER CHANNELS")
    if channels:
        st.write("### 📱 Customer Channels")
        
        # Try to extract specific parts
        online = re.search(r'ONLINE CHANNELS:(.*?)(?=OFFLINE CHANNELS:|$)', channels, re.DOTALL)
        offline = re.search(r'OFFLINE CHANNELS:(.*?)(?=INFLUENTIAL VOICES:|$)', channels, re.DOTALL)
        influencers = re.search(r'INFLUENTIAL VOICES:(.*?)(?=SOURCE:|$)', channels, re.DOTALL)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Online Channels:**")
            st.write(online.group(1).strip() if online else "Not specified")
            
            st.write("**Offline Channels:**")
            st.write(offline.group(1).strip() if offline else "Not specified")
        
        with col2:
            st.write("**Influential Voices:**")
            st.write(influencers.group(1).strip() if influencers else "Not specified")
    
    # Extract customer language and pain points
    language_pattern = r"PAIN POINT:(.*?)DIRECT QUOTES:(.*?)FREQUENCY:(.*?)SOURCE:(.*?)(?=PAIN POINT:|EXISTING SOLUTIONS:|$)"
    language_sections = list(re.finditer(language_pattern, research_data, re.DOTALL))
    
    if language_sections:
        st.write("### 💬 Customer Language & Pain Points")
        
        for i, match in enumerate(language_sections):
            pain_point = match.group(1).strip()
            quotes = match.group(2).strip()
            frequency = match.group(3).strip()
            source = match.group(4).strip() if len(match.groups()) > 3 else "Not specified"
            
            with st.expander(f"Pain Point: {pain_point}"):
                st.write("**Direct Quotes:**")
                for quote in quotes.split('\n'):
                    if quote.strip():
                        st.write(f"> *{quote.strip()}*")
                
                st.write("**Frequency:**", frequency)
                st.write("**Source:**", source)
                
                # Add a button to save to evidence
                if st.button(f"Save This Pain Point to Evidence", key=f"save_pain_{i}"):
                    from tools.evidence_tracker import EvidenceTracker
                    if 'evidence_tracker' not in st.session_state:
                        st.session_state.evidence_tracker = EvidenceTracker(storage_path='data/evidence.json')
                    
                    pain_point_info = f"""
                    Pain Point: {pain_point}
                    Direct Quotes: {quotes}
                    Frequency: {frequency}
                    Source: {source}
                    """
                    
                    st.session_state.evidence_tracker.add_evidence(
                        decision_id=f"pain_point_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        evidence_type="customer_pain_point",
                        source=source,
                        content=pain_point_info,
                        agent_name="Market Research Specialist",
                        confidence=4
                    )
                    
                    st.success(f"Saved pain point to evidence!")
    
    # Extract existing solutions
    solutions_pattern = r"SOLUTION:(.*?)USAGE:(.*?)SATISFACTION:(.*?)GAPS:(.*?)SOURCE:(.*?)(?=SOLUTION:|BUYING BEHAVIOR:|$)"
    solutions = list(re.finditer(solutions_pattern, research_data, re.DOTALL))
    
    if solutions:
        st.write("### 🔄 Existing Solutions")
        
        for i, match in enumerate(solutions):
            solution = match.group(1).strip()
            usage = match.group(2).strip()
            satisfaction = match.group(3).strip()
            gaps = match.group(4).strip()
            source = match.group(5).strip() if len(match.groups()) > 4 else "Not specified"
            
            with st.expander(f"Solution: {solution}"):
                st.write("**How Customers Use It:**", usage)
                st.write("**Satisfaction Level:**", satisfaction)
                st.write("**Gaps/Unmet Needs:**", gaps)
                st.write("**Source:**", source)
    
    # Extract buying behavior
    buying = extract_section(research_data, "BUYING BEHAVIOR")
    if buying:
        st.write("### 💰 Buying Behavior")
        
        # Try to extract specific parts
        sensitivity = re.search(r'PRICE SENSITIVITY:(.*?)(?=DECISION FACTORS:|$)', buying, re.DOTALL)
        factors = re.search(r'DECISION FACTORS:(.*?)(?=PURCHASING PROCESS:|$)', buying, re.DOTALL)
        process = re.search(r'PURCHASING PROCESS:(.*?)(?=SOURCE:|$)', buying, re.DOTALL)
        
        if sensitivity or factors or process:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Price Sensitivity:**")
                st.write(sensitivity.group(1).strip() if sensitivity else "Not specified")
                
                st.write("**Decision Factors:**")
                st.write(factors.group(1).strip() if factors else "Not specified")
            
            with col2:
                st.write("**Purchasing Process:**")
                st.write(process.group(1).strip() if process else "Not specified")
        else:
            st.write(buying)
    
    # Extract recommendations
    recommendations = extract_section(research_data, "TARGETING RECOMMENDATIONS")
    if recommendations:
        st.write("### 🎯 Targeting Recommendations")
        
        # Try to extract numbered recommendations
        rec_list = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', recommendations, re.DOTALL)
        
        if rec_list:
            for i, rec in enumerate(rec_list, 1):
                st.write(f"{i}. {rec.strip()}")
        else:
            st.write(recommendations)

def display_competitor_analysis(research_data):
    """Display competitor analysis results."""
    st.write("## Competitor Analysis Results")
    
    # Extract competitor landscape
    landscape = extract_section(research_data, "COMPETITOR LANDSCAPE")
    if landscape:
        st.write("### 🌐 Competitor Landscape")
        
        # Try to extract specific parts
        direct = re.search(r'DIRECT COMPETITORS:(.*?)(?=INDIRECT COMPETITORS:|$)', landscape, re.DOTALL)
        indirect = re.search(r'INDIRECT COMPETITORS:(.*?)(?=POTENTIAL FUTURE COMPETITORS:|$)', landscape, re.DOTALL)
        future = re.search(r'POTENTIAL FUTURE COMPETITORS:(.*?)(?=SOURCE:|$)', landscape, re.DOTALL)
        
        if direct or indirect or future:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Direct Competitors:**")
                st.write(direct.group(1).strip() if direct else "Not specified")
                
                st.write("**Indirect Competitors:**")
                st.write(indirect.group(1).strip() if indirect else "Not specified")
            
            with col2:
                st.write("**Potential Future Competitors:**")
                st.write(future.group(1).strip() if future else "Not specified")
        else:
            st.write(landscape)
    
    # Extract competitor profiles
    profile_pattern = r"NAME:(.*?)COMPANY SIZE:(.*?)FOUNDING DATE:(.*?)BUSINESS MODEL:(.*?)TARGET CUSTOMERS:(.*?)UNIQUE VALUE PROPOSITION:(.*?)KEY FEATURES:(.*?)PRICING STRATEGY:(.*?)GO-TO-MARKET STRATEGY:(.*?)STRENGTHS:(.*?)WEAKNESSES:(.*?)SOURCE:(.*?)(?=NAME:|MARKET POSITIONING:|$)"
    profiles = list(re.finditer(profile_pattern, research_data, re.DOTALL))
    
    if profiles:
        st.write("### 🏢 Competitor Profiles")
        
        competitor_names = [match.group(1).strip() for match in profiles]
        comp_tabs = st.tabs(competitor_names)
        
        for i, (match, tab) in enumerate(zip(profiles, comp_tabs)):
            with tab:
                name = match.group(1).strip()
                size = match.group(2).strip()
                founding = match.group(3).strip()
                business_model = match.group(4).strip()
                target = match.group(5).strip()
                value_prop = match.group(6).strip()
                features = match.group(7).strip()
                pricing = match.group(8).strip()
                go_to_market = match.group(9).strip()
                strengths = match.group(10).strip()
                weaknesses = match.group(11).strip()
                source = match.group(12).strip() if len(match.groups()) > 11 else "Not specified"
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Company Info")
                    st.write("**Size:**", size)
                    st.write("**Founded:**", founding)
                    st.write("**Business Model:**", business_model)
                    st.write("**Target Customers:**", target)
                    st.write("**Unique Value Proposition:**", value_prop)
                
                with col2:
                    st.markdown("#### Market Approach")
                    st.write("**Key Features:**", features)
                    st.write("**Pricing Strategy:**", pricing)
                    st.write("**Go-to-Market Strategy:**", go_to_market)
                
                st.markdown("#### SWOT Analysis")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Strengths:**")
                    for strength in strengths.split('-'):
                        if strength.strip():
                            st.write(f"✅ {strength.strip()}")
                
                with col2:
                    st.write("**Weaknesses:**")
                    for weakness in weaknesses.split('-'):
                        if weakness.strip():
                            st.write(f"⚠️ {weakness.strip()}")
                
                st.write("**Source:**", source)
                
                # Add a button to save to evidence
                if st.button(f"Save {name} Analysis to Evidence", key=f"save_comp_profile_{i}"):
                    from tools.evidence_tracker import EvidenceTracker
                    if 'evidence_tracker' not in st.session_state:
                        st.session_state.evidence_tracker = EvidenceTracker(storage_path='data/evidence.json')
                    
                    competitor_info = f"""
                    Name: {name}
                    Company Size: {size}
                    Founding Date: {founding}
                    Business Model: {business_model}
                    Target Customers: {target}
                    Unique Value Proposition: {value_prop}
                    Key Features: {features}
                    Pricing Strategy: {pricing}
                    Go-to-Market Strategy: {go_to_market}
                    Strengths: {strengths}
                    Weaknesses: {weaknesses}
                    Source: {source}
                    """
                    
                    st.session_state.evidence_tracker.add_evidence(
                        decision_id=f"competitor_profile_{name.lower().replace(' ', '_')}",
                        evidence_type="competitor_profile",
                        source=source,
                        content=competitor_info,
                        agent_name="Market Research Specialist",
                        confidence=4
                    )
                    
                    st.success(f"Saved {name} profile to evidence!")
    
    # Extract market positioning
    positioning = extract_section(research_data, "MARKET POSITIONING")
    if positioning:
        st.write("### 📊 Market Positioning")
        
        # Try to extract specific parts
        leaders = re.search(r'MARKET LEADERS:(.*?)(?=MARKET GAPS:|$)', positioning, re.DOTALL)
        gaps = re.search(r'MARKET GAPS:(.*?)(?=DIFFERENTIATION FACTORS:|$)', positioning, re.DOTALL)
        differentiation = re.search(r'DIFFERENTIATION FACTORS:(.*?)(?=SOURCE:|$)', positioning, re.DOTALL)
        
        if leaders or gaps or differentiation:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Market Leaders:**")
                st.write(leaders.group(1).strip() if leaders else "Not specified")
                
                st.write("**Market Gaps:**")
                st.write(gaps.group(1).strip() if gaps else "Not specified")
            
            with col2:
                st.write("**Differentiation Factors:**")
                st.write(differentiation.group(1).strip() if differentiation else "Not specified")
        else:
            st.write(positioning)
    
    # Extract customer feedback
    feedback_pattern = r"COMPETITOR:(.*?)POSITIVE FEEDBACK:(.*?)NEGATIVE FEEDBACK:(.*?)SOURCE:(.*?)(?=COMPETITOR:|COMPETITIVE STRATEGY:|$)"
    feedback_sections = list(re.finditer(feedback_pattern, research_data, re.DOTALL))
    
    if feedback_sections:
        st.write("### 👥 Customer Feedback Analysis")
        
        for i, match in enumerate(feedback_sections):
            competitor = match.group(1).strip()
            positive = match.group(2).strip()
            negative = match.group(3).strip()
            source = match.group(4).strip() if len(match.groups()) > 3 else "Not specified"
            
            with st.expander(f"Feedback for {competitor}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**What Customers Like:**")
                    for point in positive.split('-'):
                        if point.strip():
                            st.write(f"👍 {point.strip()}")
                
                with col2:
                    st.write("**What Customers Dislike:**")
                    for point in negative.split('-'):
                        if point.strip():
                            st.write(f"👎 {point.strip()}")
                
                st.write("**Source:**", source)
    
    # Extract competitive strategy
    strategy = extract_section(research_data, "COMPETITIVE STRATEGY")
    if strategy:
        st.write("### 🧠 Competitive Strategy Recommendations")
        
        # Try to extract numbered recommendations
        rec_list = re.findall(r'\d+\.\s*(.*?)(?=\d+\.|$)', strategy, re.DOTALL)
        
        if rec_list:
            for i, rec in enumerate(rec_list, 1):
                st.write(f"{i}. {rec.strip()}")
        else:
            st.write(strategy)

def conduct_market_research():
    """Initiate and display market research."""
    st.write("# Market Research")
    
    if 'market_research_completed' not in st.session_state:
        st.session_state.market_research_completed = False
    
    if 'market_research_in_progress' not in st.session_state:
        st.session_state.market_research_in_progress = False
    
    if 'customer_segment_research_completed' not in st.session_state:
        st.session_state.customer_segment_research_completed = False
    
    if 'competitor_analysis_completed' not in st.session_state:
        st.session_state.competitor_analysis_completed = False
    
    # Display tabs for different research types
    tabs = st.tabs(["General Market Research", "Customer Segment Analysis", "Competitor Analysis"])
    
    with tabs[0]:  # General Market Research
        if not st.session_state.market_research_completed:
            if not st.session_state.market_research_in_progress:
                if st.button("Start Market Research"):
                    st.session_state.market_research_in_progress = True
                    with st.spinner("Researching the market for your idea..."):
                        from agents.orchestrator import OrchestratorAgent
                        from agents.researcher import ResearcherAgent
                        from tools.evidence_tracker import EvidenceTracker
                        
                        # Initialize evidence tracker
                        if 'evidence_tracker' not in st.session_state:
                            st.session_state.evidence_tracker = EvidenceTracker(storage_path='data/evidence.json')
                        
                        # Get key assumptions from session state
                        assumptions = []
                        if st.session_state.key_assumptions:
                            assumptions = [a.get("assumption") for a in st.session_state.key_assumptions]
                        elif st.session_state.validations:
                            assumptions = [v.get("validation") for v in st.session_state.validations]
                        
                        # Get the idea description
                        idea_description = st.session_state.get("stored_idea_description", "")
                        
                        if not assumptions or not idea_description:
                            st.error("No assumptions or idea description available. Please complete the initial analysis first.")
                            st.session_state.market_research_in_progress = False
                            return
                        
                        # Initialize agents
                        orchestrator = OrchestratorAgent()
                        researcher = ResearcherAgent()
                        
                        # Create market research task
                        market_research_task = researcher.research_market(
                            idea_description=idea_description,
                            key_assumptions=assumptions
                        )
                        
                        # Create and run the crew
                        research_crew = orchestrator.get_research_crew(
                            orchestrator_agent=orchestrator.agent,
                            researcher_agent=researcher.agent,
                            tasks=[market_research_task]
                        )
                        
                        # Execute the crew and get results
                        result = research_crew.kickoff()
                        
                        # Store results in session state
                        st.session_state.market_research = result.raw
                        st.session_state.market_research_completed = True
                        st.session_state.market_research_in_progress = False
                        
                        # Add research findings to evidence tracker
                        st.session_state.evidence_tracker.add_evidence(
                            decision_id=f"market_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            evidence_type="market_research",
                            source="AI Research",
                            content=result.raw,
                            agent_name="Market Research Specialist",
                            confidence=4
                        )
            else:
                st.info("Market research is in progress. Please wait...")
        
        # Display market research results if available
        if st.session_state.market_research_completed and st.session_state.get("market_research"):
            display_market_research_results(st.session_state.market_research)
    
    with tabs[1]:  # Customer Segment Analysis
        if not st.session_state.customer_segment_research_completed:
            st.write("## Customer Segment Analysis")
            st.write("Analyze your target customer segment in detail.")
            
            # Form for customer segment analysis
            with st.form("customer_segment_form"):
                customer_segment = st.text_area(
                    "Describe your target customer segment",
                    placeholder="E.g., Small business owners aged 30-45 who need accounting automation"
                )
                
                pain_points = st.text_area(
                    "List potential pain points (optional)",
                    placeholder="E.g., Time spent on manual bookkeeping, difficulty tracking expenses"
                )
                
                submit_button = st.form_submit_button("Research Customer Segment")
                
                if submit_button and customer_segment:
                    with st.spinner("Researching your target customer segment..."):
                        from agents.researcher import ResearcherAgent
                        
                        # Initialize researcher
                        researcher = ResearcherAgent()
                        
                        # Create research task
                        segment_research_task = researcher.research_customer_segment(
                            customer_segment=customer_segment,
                            pain_points=pain_points
                        )
                        
                        # Execute the task
                        from crewai import Crew, Process
                        segment_crew = Crew(
                            agents=[researcher.agent],
                            tasks=[segment_research_task],
                            verbose=True,
                            process=Process.sequential
                        )
                        
                        result = segment_crew.kickoff()
                        
                        # Store results
                        st.session_state.customer_segment_research = result.raw
                        st.session_state.customer_segment_research_completed = True
                        
                        # Add to evidence tracker
                        st.session_state.evidence_tracker.add_evidence(
                            decision_id=f"segment_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            evidence_type="customer_research",
                            source="AI Research",
                            content=result.raw,
                            agent_name="Market Research Specialist",
                            confidence=4
                        )
        
        # Display customer segment research results if available
        if st.session_state.customer_segment_research_completed and st.session_state.get("customer_segment_research"):
            display_customer_segment_results(st.session_state.customer_segment_research)
    
    with tabs[2]:  # Competitor Analysis
        if not st.session_state.competitor_analysis_completed:
            st.write("## Competitor Analysis")
            st.write("Analyze your competitors in detail.")
            
            # Form for competitor analysis
            with st.form("competitor_analysis_form"):
                competitors = st.text_area(
                    "List specific competitors to analyze (optional)",
                    placeholder="E.g., QuickBooks, Xero, FreshBooks"
                )
                
                industry = st.text_input(
                    "Industry for competitive analysis",
                    placeholder="E.g., Small business accounting software"
                )
                
                submit_button = st.form_submit_button("Research Competitors")
                
                if submit_button and (competitors or industry):
                    with st.spinner("Analyzing competitors..."):
                        from agents.researcher import ResearcherAgent
                        
                        # Initialize researcher
                        researcher = ResearcherAgent()
                        
                        # Create research task
                        competitors_list = [c.strip() for c in competitors.split(",")] if competitors else None
                        competitor_task = researcher.analyze_competitors(
                            competitors=competitors_list,
                            industry=industry
                        )
                        
                        # Execute the task
                        from crewai import Crew, Process
                        competitor_crew = Crew(
                            agents=[researcher.agent],
                            tasks=[competitor_task],
                            verbose=True,
                            process=Process.sequential
                        )
                        
                        result = competitor_crew.kickoff()
                        
                        # Store results
                        st.session_state.competitor_analysis = result.raw
                        st.session_state.competitor_analysis_completed = True
                        
                        # Add to evidence tracker
                        st.session_state.evidence_tracker.add_evidence(
                            decision_id=f"competitor_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            evidence_type="competitor_analysis",
                            source="AI Research",
                            content=result.raw,
                            agent_name="Market Research Specialist",
                            confidence=4
                        )
        
        # Display competitor analysis results if available
        if st.session_state.competitor_analysis_completed and st.session_state.get("competitor_analysis"):
            display_competitor_analysis(st.session_state.competitor_analysis)

def main():
    st.set_page_config(
        page_title="Lean Startup AI Advisor",
        page_icon="🚀",
        layout="wide"
    )

    init_session_state()

    # Check if API keys are configured
    if st.session_state.project_stage == 'api_setup':
        display_api_setup()
        return

    # Sidebar navigation - only show if not in API setup
    st.sidebar.title("Lean Startup Navigator")
    
    # Only show navigation options if initial analysis is complete
    if st.session_state.current_results is not None:
        selected_stage = st.sidebar.radio(
            "Select Stage",
            ["Initial Analysis", "Market Research", "Customer Interviews", "MVP Design", "Business Model Canvas"],
            key="navigation"
        )
        
        if selected_stage == "Initial Analysis":
            st.session_state.project_stage = 'analysis_results'
        elif selected_stage == "Market Research":
            st.session_state.project_stage = 'market_research'
        elif selected_stage == "Customer Interviews":
            st.session_state.project_stage = 'customer_interviews'
        elif selected_stage == "MVP Design":
            st.session_state.project_stage = 'mvp_design'
        elif selected_stage == "Business Model Canvas":
            st.session_state.project_stage = 'bmc_review'
    
    # Add an API settings option in the sidebar
    with st.sidebar.expander("API Settings"):
        st.write("Update your API keys if needed:")
        new_openai_key = st.text_input("OpenAI API Key", value=st.session_state.openai_api_key, type="password", key="update_openai")
        new_serper_key = st.text_input("Serper API Key", value=st.session_state.serper_api_key, type="password", key="update_serper")
        
        if st.button("Update API Keys"):
            st.session_state.openai_api_key = new_openai_key
            st.session_state.serper_api_key = new_serper_key
            os.environ["OPENAI_API_KEY"] = new_openai_key
            os.environ["SERPER_API_KEY"] = new_serper_key
            st.success("API keys updated successfully!")

    # Main page content
    st.title("Lean Startup AI Advisor 🚀")
    st.subheader("Your AI-powered startup methodology guide")

    # Display appropriate content based on project stage
    if st.session_state.project_stage == 'initial':
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
            
            # Store the idea description for later use
            st.session_state.stored_idea_description = idea_description
            
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
    
    elif st.session_state.project_stage == 'analysis_results':
        # Display previously generated analysis results
        if st.session_state.current_results:
            display_analysis_results(st.session_state.current_results)
    
    elif st.session_state.project_stage == 'market_research':
        # Conduct and display market research
        conduct_market_research()
    
    elif st.session_state.project_stage == 'customer_interviews':
        # Display customer interview interface
        display_customer_interviews()
    
    elif st.session_state.project_stage == 'mvp_design':
        # Display MVP design interface
        display_mvp_design()
    
    elif st.session_state.project_stage == 'bmc_review':
        # Display BMC review interface
        display_bmc_review()

if __name__ == "__main__":
    main()