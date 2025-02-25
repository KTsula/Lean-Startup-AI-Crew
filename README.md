# Lean Startup AI Advisor

An AI-powered assistant for entrepreneurs applying the Lean Startup methodology. This application uses a multi-agent system built with CrewAI to guide users through the startup process, from idea validation to MVP design.

## Features

- **Initial Idea Analysis**: Analyze business ideas through the lens of Lean Startup methodology
- **Market Research**: Gather competitive intelligence and market data from the web
- **Business Model Canvas**: Create and iterate on your business model
- **Hypothesis Testing**: Design customer interviews and experiments to validate your assumptions
- **MVP Planning**: Design a minimum viable product based on validated learnings
- **Human-in-the-Loop Validation**: Incorporate real customer feedback into the process

## Getting Started

### Prerequisites

- Python 3.10 or higher
- API keys for OpenAI and SerperDev

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/lean-startup-ai.git
cd lean-startup-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
```

### Running the Application

Start the Streamlit app:
```bash
streamlit run src/main.py
```

The application will be available at http://localhost:8501

## Usage Guide

1. **Initial Analysis**:
   - Enter your startup idea, customer segment, or pain point
   - The AI will analyze your input and identify key assumptions, risks, and next steps
   - Review the Business Model Canvas generated based on your idea

2. **Market Research**:
   - Click on "Conduct Market Research" to have the AI research your market
   - Review findings about market size, competitors, customer insights, and pricing models
   - See how market evidence validates or invalidates your assumptions

3. **Customer Interviews**:
   - Use the AI-generated validation plan to conduct customer interviews
   - Record your findings and evidence from real customers
   - Get recommendations based on your validation results

4. **MVP Design**:
   - Design your Minimum Viable Product based on validated assumptions
   - Define core features, success metrics, and resource requirements
   - Plan your development timeline

5. **Business Model Canvas**:
   - Review and edit your Business Model Canvas
   - Update it based on learnings from research and validation

## Architecture

The application uses CrewAI to orchestrate multiple specialized AI agents:

- **Orchestrator Agent**: Guides the overall process and applies Lean Startup methodology
- **Researcher Agent**: Gathers market data and competitive intelligence
- **Business Model Canvas Agent**: Creates and updates the business model
- **Validation Agent**: Designs experiments and interview questions

The agents work together to provide comprehensive guidance throughout the startup journey.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- This project uses the [CrewAI](https://github.com/crewAI/crewAI) framework
- Based on the Lean Startup methodology by Eric Ries