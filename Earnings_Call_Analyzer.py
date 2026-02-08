

import asyncio
import json
import os
import base64
import time
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

OLLAMA_AVAILABLE = False
try:
    import ollama
    ollama.list()
    OLLAMA_AVAILABLE = True
except:
    pass

if not ANTHROPIC_API_KEY and __name__ == "__main__" and not os.environ.get("SKIP_PROMPTS"):
    print("\n" + "="*60)
    print(" SELECT AI ENGINE")
    print("="*60)
    print("\n OPTION 1: CLAUDE API (Best Quality)")
    print("   - Claude Sonnet 4 (most intelligent)")
    print("   - Fully automated")
    print("   - Cost: ~$0.10 per analysis")
    print("   - Setup: Need API key from console.anthropic.com")
    print("\n OPTION 2: OLLAMA (Free & Automated)")
    print("   - Llama 3.1 (runs on your computer)")
    print("   - Fully automated")
    print("   - Cost: $0 (completely free)")
    if OLLAMA_AVAILABLE:
        print("    Ollama detected and ready!")
    else:
        print("    Not installed - Get from: https://ollama.com")
    print("\n OPTION 3: DEMO MODE")
    print("   - Pre-loaded sample analyses")
    print("   - Instant results")
    print("   - No AI needed")
    print("\n" + "="*60)

    user_input = input("\nEnter API key, type 'ollama', or press Enter for demo: ").strip().lower()

    if user_input and user_input != 'ollama':
        ANTHROPIC_API_KEY = user_input
        print("\n CLAUDE API MODE ACTIVATED")
        print("   Using Claude Sonnet 4 for analysis")
    elif user_input == 'ollama':
        if OLLAMA_AVAILABLE:
            print("\n OLLAMA MODE ACTIVATED")
            print("   Using Llama 3.1 (free local AI)")
        else:
            print("\n Ollama not available!")
            print("   Install from: https://ollama.com")
            print("   Then run: ollama pull llama3.1")
            print("\n   Using DEMO MODE (samples only)")
            OLLAMA_AVAILABLE = False
    else:
        print("\n DEMO MODE ACTIVATED")
        print("   Using pre-loaded sample analyses")

USE_REAL_API = bool(ANTHROPIC_API_KEY)
USE_OLLAMA = OLLAMA_AVAILABLE and not USE_REAL_API

if USE_REAL_API:
    try:
        import anthropic
        print("Claude API ready (Sonnet 4)")
    except ImportError:
        print(" Install: pip install anthropic")
        USE_REAL_API = False
elif USE_OLLAMA:
    print("Ollama ready (Llama 3.1 - Free)")
else:
    print(" Demo mode - Use samples for instant results")

SAMPLE_ANALYSES = {
    "techcorp_q3_2025": {
        "company": "TechCorp Inc - Q3 2025",
        "revenue": {
            "score": 8.2,
            "verdict": "STRONG",
            "key_metrics": {
                "revenue": "$2.8B (up 23% YoY)",
                "guidance": "$3.2B next quarter (beat consensus)",
                "customer_growth": "+1,200 enterprise customers",
                "arr": "$10.5B (up 27% YoY)"
            },
            "highlights": [
                "Revenue beat analyst estimates by $150M (5.7%)",
                "Strong international growth - EMEA up 31% YoY",
                "Raised full-year guidance from $11B to $11.5B",
                "Enterprise segment growing faster than SMB"
            ],
            "concerns": [
                "Customer acquisition costs increased 12%",
                "SMB segment growth slowing (8% vs 15% last quarter)"
            ]
        },
        "profitability": {
            "score": 6.5,
            "verdict": "MIXED",
            "key_metrics": {
                "gross_margin": "72% (down from 74%)",
                "operating_margin": "18% (down from 21%)",
                "net_income": "$420M (up 8% YoY)",
                "free_cash_flow": "$580M (up 22%)"
            },
            "highlights": [
                "Operating expenses well-controlled, up only 9% vs 23% revenue growth",
                "Free cash flow beat expectations significantly",
                "R&D efficiency improving"
            ],
            "concerns": [
                "Gross margin compression due to infrastructure costs",
                "Operating margin trending down for 3 consecutive quarters",
                "Q4 guidance implies further margin compression to 16%"
            ]
        },
        "management": {
            "score": 7.8,
            "verdict": "CONFIDENT",
            "key_metrics": {
                "tone": "Bullish and confident",
                "defensiveness": "Low",
                "transparency": "8.5/10"
            },
            "highlights": [
                "CEO used 'confident' 12 times, 'excited' 8 times",
                "Specific details on Q4 pipeline - $800M qualified deals",
                "CEO bought $2M shares last month",
                "Directly addressed margin pressure with concrete plan"
            ],
            "concerns": [
                "Avoided question about Microsoft competition",
                "Mentioned 'macroeconomic headwinds' 5 times",
                "Vague on international expansion timeline"
            ]
        }
    }
}

class MessageType(Enum):
    ANALYSIS = "analysis"
    CHALLENGE = "challenge"
    QUESTION = "question"
    CONSENSUS = "consensus"

@dataclass
class Message:
    sender: str
    recipients: List[str]
    msg_type: MessageType
    content: str
    data: Optional[Dict] = None
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

class MessageBus:

    def __init__(self):
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List] = {}

    async def publish(self, message: Message):
        self.messages.append(message)

        if "all" in message.recipients:
            recipients = list(self.subscribers.keys())
        else:
            recipients = message.recipients

        for recipient in recipients:
            if recipient in self.subscribers and recipient != message.sender:
                for callback in self.subscribers[recipient]:
                    await callback(message)

    def subscribe(self, agent_id: str, callback):
        if agent_id not in self.subscribers:
            self.subscribers[agent_id] = []
        self.subscribers[agent_id].append(callback)

    def get_history(self) -> List[Message]:
        return self.messages

class AIAPI:

    def __init__(self, api_key: str = None, use_ollama: bool = False):
        self.use_real = USE_REAL_API and api_key
        self.use_ollama = use_ollama or (USE_OLLAMA and not self.use_real)

        if self.use_real:
            self.client = anthropic.Anthropic(api_key=api_key)
        elif self.use_ollama:
            try:
                import ollama
                self.ollama = ollama
            except ImportError:
                print(" Ollama not available, using mock")
                self.use_ollama = False

    async def analyze_document(
        self,
        system_prompt: str,
        user_prompt: str,
        document_base64: str = None,
        document_type: str = "application/pdf",
        max_tokens: int = 3000
    ) -> str:

        # MODE 1: Claude API
        if self.use_real:
            try:
                content = []

                if document_base64:
                    content.append({
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": document_type,
                            "data": document_base64
                        }
                    })

                content.append({"type": "text", "text": user_prompt})

                response = self.client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": content}]
                )

                return response.content[0].text

            except Exception as e:
                print(f"  API Error: {e}")
                print(f"  Error type: {type(e).__name__}")
                print(f"  Falling back to mock.")
                import traceback
                traceback.print_exc()
                return self._mock_response(user_prompt)

        # MODE 2: Ollama (Free Local AI)
        elif self.use_ollama:
            try:
                full_prompt = f"{system_prompt}\n\n{user_prompt}"

                print("  Calling Ollama (local AI)...")
                response = self.ollama.chat(
                    model='llama3.1',
                    messages=[{'role': 'user', 'content': full_prompt}]
                )

                return response['message']['content']

            except Exception as e:
                print(f"  Ollama Error: {e}. Falling back to mock.")
                return self._mock_response(user_prompt)

        # MODE 3: Mock (for demo/testing)
        else:
            await asyncio.sleep(0.8)
            return self._mock_response(user_prompt)

    def _mock_response(self, prompt: str) -> str:
        print(f"  Using mock response for: {prompt[:50]}...")

        if "revenue" in prompt.lower():
            return """{
                "score": 8.2,
                "verdict": "STRONG",
                "key_metrics": {
                    "revenue": "$2.8B (up 23% YoY)",
                    "guidance": "$3.2B next quarter",
                    "customer_growth": "+1,200 enterprise customers",
                    "arr": "$10.5B (up 27% YoY)"
                },
                "highlights": [
                    "Revenue beat analyst estimates by $150M (5.7%)",
                    "Strong international growth - EMEA up 31% YoY",
                    "Raised full-year guidance"
                ],
                "concerns": [
                    "Customer acquisition costs increased 12%",
                    "SMB segment growth slowing"
                ]
            }"""

        elif "profitability" in prompt.lower() or "margin" in prompt.lower():
            return """{
                "score": 6.5,
                "verdict": "MIXED",
                "key_metrics": {
                    "gross_margin": "72% (down from 74%)",
                    "operating_margin": "18% (down from 21%)",
                    "net_income": "$420M (up 8% YoY)",
                    "free_cash_flow": "$580M (up 22%)"
                },
                "highlights": [
                    "Operating expenses well-controlled",
                    "Free cash flow beat expectations",
                    "R&D efficiency improving"
                ],
                "concerns": [
                    "Gross margin compression",
                    "Operating margin trending down",
                    "Q4 guidance implies further compression"
                ]
            }"""

        elif "management" in prompt.lower():
            return """{
                "score": 7.8,
                "verdict": "CONFIDENT",
                "key_metrics": {
                    "tone": "Bullish and confident",
                    "defensiveness": "Low",
                    "transparency": "8.5/10"
                },
                "positive_signals": [
                    "CEO used confident language frequently",
                    "Specific pipeline details provided",
                    "CEO insider buying signal"
                ],
                "red_flags": [
                    "Avoided competitive questions",
                    "Some hedging language present"
                ]
            }"""

        else:
            return '{"score": 7.0, "verdict": "NEUTRAL"}'

def clean_ollama_json(json_str: str) -> str:
    # Fix unquoted percentage values: 72% -> "72%"
    json_str = re.sub(r':\s*(\d+%)', r': "\1"', json_str)

    # Fix unquoted numbers that should be strings in key_metrics
    # Match patterns like: "revenue": 2.8B -> "revenue": "2.8B"
    json_str = re.sub(r':\s*([0-9.]+[BMK])\s*([,\}])', r': "\1"\2', json_str)

    # Fix boolean True/False to true/false
    json_str = json_str.replace('True', 'true').replace('False', 'false')

    # Fix None to null
    json_str = json_str.replace('None', 'null')

    return json_str

def safe_json_parse(response: str, fallback_prompt: str, ai_instance) -> dict:
    try:
        # Strategy 1: Direct JSON parse
        return json.loads(response)
    except:
        pass

    try:
        # Strategy 2: Extract from markdown code blocks
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0].strip()
        else:
            # Strategy 3: Find JSON object with regex
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group()
            else:
                raise ValueError("No JSON found")

        # Clean Ollama-specific issues
        json_str = clean_ollama_json(json_str)
        return json.loads(json_str)

    except Exception as e:
        print(f"  All JSON parse strategies failed: {e}")
        print(f"  Raw response preview: {response[:300]}...")
        return json.loads(ai_instance._mock_response(fallback_prompt))

class EarningsAgent:

    def __init__(
        self,
        agent_id: str,
        expertise: str,
        message_bus: MessageBus,
        ai_api: AIAPI
    ):
        self.agent_id = agent_id
        self.expertise = expertise
        self.message_bus = message_bus
        self.ai = ai_api

        self.analysis: Dict = {}
        self.score: float = 0.0
        self.inbox: List[Message] = []

        self.message_bus.subscribe(agent_id, self.receive_message)

    async def receive_message(self, message: Message):
        self.inbox.append(message)

        if message.msg_type == MessageType.CHALLENGE:
            await self.handle_challenge(message)

    async def send_message(
        self,
        recipients: List[str],
        msg_type: MessageType,
        content: str,
        data: Dict = None
    ):
        message = Message(
            sender=self.agent_id,
            recipients=recipients,
            msg_type=msg_type,
            content=content,
            data=data
        )
        await self.message_bus.publish(message)

    async def broadcast_analysis(self, analysis: Dict):
        await self.send_message(
            recipients=["all"],
            msg_type=MessageType.ANALYSIS,
            content=f"{self.agent_id} completed analysis - Score: {self.score}/10",
            data=analysis
        )

    async def challenge_peer(self, peer_id: str, concern: str):
        await self.send_message(
            recipients=[peer_id],
            msg_type=MessageType.CHALLENGE,
            content=concern
        )

    async def handle_challenge(self, message: Message):
        print(f"  [{self.agent_id}] Received challenge: {message.content}")

        import random
        if random.random() > 0.7:
            old_score = self.score
            self.score *= 0.9
            print(f"  [{self.agent_id}] Revised score: {old_score:.1f} → {self.score:.1f}")

class RevenueAgent(EarningsAgent):

    def __init__(self, message_bus: MessageBus, ai_api: AIAPI):
        super().__init__("revenue_agent", "Revenue Analysis", message_bus, ai_api)

    async def analyze(
        self,
        document_text: str = None,
        document_base64: str = None
    ) -> Dict:
        print(f"\n[{self.agent_id}] Analyzing revenue metrics...")

        prompt = """
        Analyze the REVENUE performance from this earnings report.
        
        Focus on:
        1. Revenue growth (actual vs estimates vs guidance)
        2. Revenue guidance for next quarter/year
        3. Customer acquisition and retention metrics
        4. Geographic/segment breakdown
        5. ARR/MRR trends (if SaaS)
        
        CRITICAL: Return ONLY valid JSON with this EXACT structure.
        ALL values must be properly quoted strings or numbers.
        Do NOT use unquoted percentages or currency symbols.
        
        {
            "score": 7.5,
            "verdict": "STRONG",
            "key_metrics": {
                "revenue": "actual revenue with growth percent",
                "guidance": "forward guidance",
                "customer_growth": "customer metrics",
                "arr": "ARR if applicable"
            },
            "highlights": ["positive point 1", "positive point 2"],
            "concerns": ["extract specific risk factor 1", "extract specific risk factor 2"]
        }
        
        Return ONLY the JSON object. No markdown formatting. No explanations.
        """

        if document_text:
            prompt = f"{prompt}\n\nDocument text:\n{document_text[:3000]}"

        response = await self.ai.analyze_document(
            system_prompt="You are a revenue analysis expert for public companies. Focus on top-line growth.",
            user_prompt=prompt,
            document_base64=document_base64
        )

        analysis = safe_json_parse(response, "revenue", self.ai)

        self.analysis = analysis
        try:
            self.score = float(analysis.get('score', 7.0))
        except:
            self.score = 7.0

        await self.broadcast_analysis(analysis)
        await asyncio.sleep(0.3)

        return analysis


class ProfitabilityAgent(EarningsAgent):

    def __init__(self, message_bus: MessageBus, ai_api: AIAPI):
        super().__init__("profitability_agent", "Profitability Analysis", message_bus, ai_api)

    async def analyze(
        self,
        document_text: str = None,
        document_base64: str = None
    ) -> Dict:
        print(f"\n[{self.agent_id}] Analyzing profitability metrics...")

        prompt = """
        Analyze the PROFITABILITY and MARGINS from this earnings report.
        
        Focus on: Gross margin, operating margin, net income, free cash flow, cost efficiency
        
        CRITICAL: Return ONLY valid JSON. ALL values must be quoted strings.
        Do NOT use unquoted percentages (72%) - use strings ("72%").
        
        {
            "score": 6.5,
            "verdict": "MIXED",
            "key_metrics": {
                "gross_margin": "percent as string",
                "operating_margin": "percent as string", 
                "net_income": "dollar amount as string",
                "free_cash_flow": "dollar amount as string"
            },
            "highlights": ["positive point 1", "positive point 2"],
            "concerns": ["extract specific risk factor 1", "extract specific risk factor 2"]
        }
        
        Return ONLY the JSON object. No markdown. No explanations.
        """

        if document_text:
            prompt = f"{prompt}\n\nDocument text:\n{document_text[:3000]}"

        response = await self.ai.analyze_document(
            system_prompt="You are a profitability analysis expert. Focus on margins and efficiency.",
            user_prompt=prompt,
            document_base64=document_base64
        )

        analysis = safe_json_parse(response, "profitability", self.ai)

        self.analysis = analysis
        try:
            self.score = float(analysis.get('score', 6.5))
        except:
            self.score = 6.5

        await self.broadcast_analysis(analysis)
        await asyncio.sleep(0.3)

        # Challenge revenue agent if needed
        revenue_messages = [m for m in self.inbox if m.sender == "revenue_agent"]
        if revenue_messages and self.score < 7.0:
            revenue_data = revenue_messages[0].data
            if revenue_data and revenue_data.get('score', 0) > 8.0:
                await self.challenge_peer(
                    "revenue_agent",
                    "Revenue growth is impressive, but margin compression is concerning."
                )

        return analysis


class ManagementAgent(EarningsAgent):

    def __init__(self, message_bus: MessageBus, ai_api: AIAPI):
        super().__init__("management_agent", "Management Analysis", message_bus, ai_api)

    async def analyze(
        self,
        document_text: str = None,
        document_base64: str = None
    ) -> Dict:
        print(f"\n[{self.agent_id}] Analyzing management commentary...")

        prompt = """
        Analyze MANAGEMENT TONE and CREDIBILITY from this earnings call.
        
        Focus on: CEO/CFO confidence, forward-looking statements, red flags, track record
        
        CRITICAL: Return ONLY valid JSON. ALL values must be quoted strings.
        
        {
            "score": 7.8,
            "verdict": "CONFIDENT",
            "key_metrics": {
                "tone": "description of tone",
                "defensiveness": "Low/Medium/High",
                "transparency": "rating out of 10"
            },
            "positive_signals": ["signal 1", "signal 2"],
            "red_flags": ["quote specific evasive answer", "quote hesitation or vagueness"]
        }
        
        Return ONLY the JSON object. No markdown. No explanations.
        """

        if document_text:
            prompt = f"{prompt}\n\nDocument text:\n{document_text[:3000]}"

        response = await self.ai.analyze_document(
            system_prompt="You are an expert at reading executive communications. Detect confidence and red flags.",
            user_prompt=prompt,
            document_base64=document_base64
        )

        analysis = safe_json_parse(response, "management", self.ai)

        self.analysis = analysis
        try:
            self.score = float(analysis.get('score', 7.5))
        except:
            self.score = 7.5

        await self.broadcast_analysis(analysis)

        return analysis

class EarningsConsensus:
    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus

    async def build_consensus(self, agents: List[EarningsAgent]) -> Dict:
        print(f"\n{'='*60}")
        print("BUILDING CONSENSUS")
        print(f"{'='*60}\n")

        print("Agent Scores:")
        agent_scores = {}
        for agent in agents:
            verdict = agent.analysis.get('verdict', 'N/A')
            print(f"  {agent.expertise}: {agent.score:.1f}/10 ({verdict})")
            agent_scores[agent.expertise] = {
                "score": agent.score,
                "verdict": verdict
            }

        # Calculate weighted average
        weights = {
            'revenue_agent': 0.40,
            'profitability_agent': 0.35,
            'management_agent': 0.25
        }

        weighted_score = sum(
            agent.score * weights[agent.agent_id]
            for agent in agents
        )

        # Determine verdict
        if weighted_score >= 8.0:
            verdict = "BEAT EXPECTATIONS - STRONG BUY"
        elif weighted_score >= 7.0:
            verdict = "MET EXPECTATIONS - HOLD/BUY"
        elif weighted_score >= 6.0:
            verdict = "MIXED RESULTS - HOLD"
        elif weighted_score >= 5.0:
            verdict = "MISSED EXPECTATIONS - HOLD/SELL"
        else:
            verdict = "POOR RESULTS - SELL"

        # Check for red flags
        red_flags = []
        messages = self.message_bus.get_history()
        challenges = [m for m in messages if m.msg_type == MessageType.CHALLENGE]
        if len(challenges) >= 2:
            red_flags.append("Multiple agents raised concerns")

        profitability = next((a for a in agents if a.agent_id == "profitability_agent"), None)
        revenue = next((a for a in agents if a.agent_id == "revenue_agent"), None)
        if profitability and revenue:
            if profitability.score < 6.5 and revenue.score > 8.0:
                red_flags.append("Strong revenue but weak margins - growth may not be profitable")

        if not red_flags:
            red_flags = ["None detected"]

        consensus = {
            "overall_score": round(weighted_score, 1),
            "verdict": verdict,
            "confidence": "High" if len(challenges) == 0 else "Medium" if len(challenges) == 1 else "Low",
            "agent_scores": agent_scores,
            "red_flags": red_flags,
            "recommendation": self._generate_recommendation(weighted_score, agents)
        }

        print(f"\n{'='*60}")
        print(f"FINAL VERDICT: {verdict}")
        print(f"Overall Score: {weighted_score:.1f}/10")
        print(f"{'='*60}\n")

        return consensus

    def _generate_recommendation(self, score: float, agents: List[EarningsAgent]) -> str:
        if score >= 8.0:
            return "Strong beat across the board. Consider buying on any dips."
        elif score >= 7.0:
            return "Solid results but not spectacular. Hold position or add on weakness."
        elif score >= 6.0:
            return "Mixed results. Monitor closely. Hold current position."
        else:
            return "Results fell short. Consider reducing position."

class EarningsAnalyzer:

    def __init__(self, api_key: str = None):
        self.ai_api = AIAPI(
            api_key=api_key or ANTHROPIC_API_KEY,
            use_ollama=USE_OLLAMA
        )
        self.message_bus = MessageBus()
        self.agents = [
            RevenueAgent(self.message_bus, self.ai_api),
            ProfitabilityAgent(self.message_bus, self.ai_api),
            ManagementAgent(self.message_bus, self.ai_api)
        ]
        self.consensus_engine = EarningsConsensus(self.message_bus)
        self.samples = SAMPLE_ANALYSES

    async def analyze_document(
        self,
        file_path: str = None,
        text_content: str = None
    ) -> Dict:
        print(f"\n{'='*60}")
        print("EARNINGS ANALYZER - AGENT SWARM")
        print(f"{'='*60}")

        # Read file if provided
        document_base64 = None
        if file_path:
            print(f"Reading file: {file_path}")
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
                document_base64 = base64.b64encode(file_bytes).decode()

        # Run agents
        print("\n--- PHASE 1: AGENT ANALYSIS ---")
        analyses = await asyncio.gather(*[
            agent.analyze(
                document_text=text_content,
                document_base64=document_base64
            )
            for agent in self.agents
        ])

        # Build consensus
        print("\n--- PHASE 2: CONSENSUS BUILDING ---")
        consensus = await self.consensus_engine.build_consensus(self.agents)

        report = {
            "timestamp": datetime.now().isoformat(),
            "consensus": consensus,
            "detailed_analysis": {
                "revenue": analyses[0],
                "profitability": analyses[1],
                "management": analyses[2]
            }
        }

        return report

async def interactive_menu():
    analyzer = EarningsAnalyzer()
    # ... rest of menu code unchanged ...

if __name__ == "__main__":
    asyncio.run(interactive_menu())