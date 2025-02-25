# src/agents/researcher.py
from crewai import Agent, Task
from crewai_tools import SerperDevTool, WebsiteSearchTool, ScrapeWebsiteTool, FileReadTool

class ResearcherAgent:
    def __init__(self):
        # Enhanced tools for the researcher
        self.tools = [
            SerperDevTool(),
            WebsiteSearchTool(),
            ScrapeWebsiteTool(),
            FileReadTool()  # For reading uploaded files from user validation
        ]
        self.agent = Agent(
            role='Market Research Specialist',
            goal='Gather comprehensive market data and competitor information to validate startup ideas',
            backstory="""You are an expert market researcher with a deep understanding 
            of startup ecosystems. Your specialty is finding relevant market data, 
            competitor information, and user trends to help validate or invalidate 
            business assumptions. You always provide evidence to support your findings
            and cite your sources clearly. You are methodical and thorough, leaving no 
            stone unturned in your research.""",
            verbose=True,
            tools=self.tools
        )

    def research_market(self, idea_description, key_assumptions, industry=None):
        """Create a task to research the market based on the idea and assumptions."""
        market_research_task = Task(
            description=f"""Research the market potential and competitive landscape for this idea:
            {idea_description}

            Focus specifically on validating these key assumptions:
            {key_assumptions}

            Industry focus (if specified): {industry if industry else 'Not specified'}

            Follow this exact process:
            1. First, search for market size and growth trends for this type of business
               MARKET SIZE AND TRENDS: <your findings with sources>

            2. Identify and analyze 3-5 similar companies or direct competitors
               COMPETITOR ANALYSIS:
               COMPETITOR: <name>
               DESCRIPTION: <what they do>
               STRENGTHS: <their advantages>
               WEAKNESSES: <their disadvantages>
               BUSINESS MODEL: <how they make money>
               MARKET SHARE: <estimated market share if available>
               TARGET AUDIENCE: <their customer segments>
               SOURCE: <where you found this information>

            3. Find information about customer behavior and preferences in this market
               CUSTOMER INSIGHTS:
               PAIN POINT: <specific customer pain point>
               EVIDENCE: <evidence this pain point exists>
               CUSTOMER QUOTE: <direct quote from customer if available>
               SOURCE: <where you found this information>

            4. Research pricing models used by similar services
               PRICING MODELS:
               MODEL TYPE: <subscription, one-time, freemium, etc>
               PRICE RANGE: <typical price points>
               VALUE METRICS: <what customers are willing to pay for>
               COMPETITOR EXAMPLES: <specific examples>
               SOURCE: <where you found this information>

            5. Identify any relevant regulations or legal considerations
               REGULATORY FACTORS: <findings with sources>

            6. Research current market trends and future projections
               MARKET TRENDS:
               TREND: <specific trend>
               EVIDENCE: <supporting data>
               IMPACT ON BUSINESS: <how it affects the business idea>
               SOURCE: <where you found this information>

            7. Based on your research, validate or challenge each assumption:
               ASSUMPTION VALIDATION:
               ASSUMPTION: <assumption>
               EVIDENCE: <supporting/contradicting evidence>
               CONCLUSION: <validated/partially validated/invalidated>
               CONFIDENCE: <high/medium/low>
               SOURCES: <list of sources>

            8. Provide specific recommendations based on your findings:
               RECOMMENDATIONS:
               1. <recommendation>
               2. <recommendation>
               ...

            For every piece of information, cite your sources clearly using URLs or references.
            Be thorough and objective, focusing on facts rather than opinions.
            
            Always use specific numbers and percentages when available.
            
            Your final output should be structured exactly according to the sections above,
            with clear headings for each section.
            """,
            expected_output="""A comprehensive market research report with clear sections for:
            - Market size and trends
            - Competitor analysis
            - Customer insights
            - Pricing models
            - Regulatory factors
            - Market trends
            - Assumption validation with evidence
            - Recommendations
            
            Each section should include specific data points and properly cited sources.""",
            agent=self.agent
        )
        
        return market_research_task
        
    def research_customer_segment(self, customer_segment, pain_points=None):
        """Create a task to research a specific customer segment in depth."""
        segment_research_task = Task(
            description=f"""Conduct in-depth research on this customer segment:
            {customer_segment}

            {f'Potential pain points to consider: {pain_points}' if pain_points else ''}

            Follow this exact process:
            1. First, define the demographic and psychographic profile of this segment
               SEGMENT PROFILE:
               DEMOGRAPHICS: <age, gender, location, income, etc.>
               PSYCHOGRAPHICS: <values, interests, lifestyle, behaviors>
               MARKET SIZE: <size of this segment>
               GROWTH TRENDS: <growth or decline of this segment>
               SOURCE: <where you found this information>

            2. Research where these customers typically hang out online and offline
               CUSTOMER CHANNELS:
               ONLINE CHANNELS: <websites, forums, social media>
               OFFLINE CHANNELS: <events, locations, communities>
               INFLUENTIAL VOICES: <thought leaders, influencers>
               SOURCE: <where you found this information>

            3. Find examples of actual customer language and pain points
               CUSTOMER LANGUAGE:
               PAIN POINT: <specific pain point>
               DIRECT QUOTES: <how customers describe this in their own words>
               FREQUENCY: <how often this is mentioned>
               SOURCE: <where you found this information>

            4. Research existing solutions this segment is using
               EXISTING SOLUTIONS:
               SOLUTION: <product or service name>
               USAGE: <how they're using it>
               SATISFACTION: <satisfaction level>
               GAPS: <unmet needs>
               SOURCE: <where you found this information>

            5. Identify willingness to pay and buying behavior
               BUYING BEHAVIOR:
               PRICE SENSITIVITY: <high/medium/low>
               DECISION FACTORS: <what influences buying decisions>
               PURCHASING PROCESS: <how they make buying decisions>
               SOURCE: <where you found this information>

            6. Provide specific recommendations for targeting this segment:
               TARGETING RECOMMENDATIONS:
               1. <recommendation>
               2. <recommendation>
               ...

            For every piece of information, cite your sources clearly using URLs or references.
            Be thorough and objective, focusing on facts rather than opinions.
            
            Your final output should be structured exactly according to the sections above,
            with clear headings for each section.
            """,
            expected_output="""A comprehensive customer segment analysis with clear sections for:
            - Segment profile
            - Customer channels
            - Customer language
            - Existing solutions
            - Buying behavior
            - Targeting recommendations
            
            Each section should include specific data points and properly cited sources.""",
            agent=self.agent
        )
        
        return segment_research_task
    
    def analyze_competitors(self, competitors=None, industry=None):
        """Create a task to analyze specific competitors or competitors in an industry."""
        competitors_str = ", ".join(competitors) if competitors and isinstance(competitors, list) else "not specified"
        
        competitor_analysis_task = Task(
            description=f"""Conduct a detailed competitive analysis for:
            
            Specific competitors to analyze: {competitors_str}
            Industry: {industry if industry else 'Not specified'}

            Follow this exact process:
            1. First, identify the main competitors in this space
               COMPETITOR LANDSCAPE:
               DIRECT COMPETITORS: <list of direct competitors>
               INDIRECT COMPETITORS: <list of indirect competitors>
               POTENTIAL FUTURE COMPETITORS: <emerging players>
               SOURCE: <where you found this information>

            2. For each major competitor, analyze in detail:
               COMPETITOR PROFILE:
               NAME: <competitor name>
               COMPANY SIZE: <employees, funding if available>
               FOUNDING DATE: <when founded>
               BUSINESS MODEL: <how they make money>
               TARGET CUSTOMERS: <who they serve>
               UNIQUE VALUE PROPOSITION: <what makes them unique>
               KEY FEATURES: <main product/service features>
               PRICING STRATEGY: <pricing details>
               GO-TO-MARKET STRATEGY: <how they acquire customers>
               STRENGTHS: <competitive advantages>
               WEAKNESSES: <limitations or disadvantages>
               SOURCE: <where you found this information>

            3. Analyze market positioning:
               MARKET POSITIONING:
               MARKET LEADERS: <who dominates and why>
               MARKET GAPS: <underserved segments or needs>
               DIFFERENTIATION FACTORS: <how companies differentiate>
               SOURCE: <where you found this information>

            4. Review customer feedback:
               CUSTOMER FEEDBACK:
               COMPETITOR: <name>
               POSITIVE FEEDBACK: <what customers like>
               NEGATIVE FEEDBACK: <what customers dislike>
               SOURCE: <where you found this information>

            5. Provide specific competitive strategy recommendations:
               COMPETITIVE STRATEGY:
               1. <recommendation>
               2. <recommendation>
               ...

            For every piece of information, cite your sources clearly using URLs or references.
            Be thorough and objective, focusing on facts rather than opinions.
            
            Your final output should be structured exactly according to the sections above,
            with clear headings for each section.
            """,
            expected_output="""A comprehensive competitive analysis with clear sections for:
            - Competitor landscape
            - Detailed competitor profiles
            - Market positioning
            - Customer feedback analysis
            - Competitive strategy recommendations
            
            Each section should include specific data points and properly cited sources.""",
            agent=self.agent
        )
        
        return competitor_analysis_task