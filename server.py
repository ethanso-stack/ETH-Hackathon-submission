import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

os.environ.setdefault("SKIP_PROMPTS", "1")

from Earnings_Call_Analyzer import EarningsAnalyzer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = EarningsAnalyzer()

class AnalysisRequest(BaseModel):
    text: str

@app.get("/")
def read_root():
    return {"message": "Earnings Analyzer API is running on Port 8001"}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "components": {
            "ai_engine": "active",
            "backend": "online"
        }
    }

@app.get("/api/samples")
def get_samples():
    samples_list = []
    if hasattr(analyzer, 'samples'):
        for key, data in analyzer.samples.items():
            score = 0
            if "consensus" in data:
                score = data["consensus"].get("overall_score", 0)
            elif "revenue" in data: 
                 score = data["revenue"].get("score", 0)
                 
            samples_list.append({
                "key": key,
                "company": data.get("company", "Unknown Sample"),
                "overall_score": score
            })
    return {"count": len(samples_list), "samples": samples_list}

@app.get("/api/sample/{sample_key}")
async def get_sample_detail(sample_key: str):
    if not hasattr(analyzer, 'samples') or sample_key not in analyzer.samples:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    raw_data = analyzer.samples[sample_key]

    if "consensus" not in raw_data:
        return {
            "company": raw_data.get("company", "Unknown Sample"),
            
            "consensus": {
                "overall_score": raw_data.get("revenue", {}).get("score", 0), 
                "verdict": "STRONG (Sample)",
                "confidence": "High", 
                "recommendation": "This is a pre-loaded sample.",
                "red_flags": ["None detected"]
            },
            
            "detailed_analysis": raw_data
        }
            
    return raw_data

@app.post("/api/analyze")
async def analyze_earnings(request: AnalysisRequest):
    print(f"Received analysis request: {len(request.text)} chars")
    
    if len(request.text) < 10:
        raise HTTPException(status_code=400, detail="Text too short (min 10 chars)")

    try:
        report = await analyzer.analyze_document(text_content=request.text)
        return report
    except Exception as e:
        print(f"Analysis Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("AI Middleware Server Started...")
    print("Listening for frontend requests on http://0.0.0.0:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)