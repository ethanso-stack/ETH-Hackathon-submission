const fileInput = document.getElementById('fileInput');
const customBtn = document.getElementById('customBtn');
const fileDisplayArea = document.getElementById('fileDisplayArea');
const analyzeBtn = document.getElementById('analyzeBtn'); 
const analysisResult = document.getElementById('analysis-result');

let extractedText = "";

// Initialize PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// Trigger file input
customBtn.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type === "application/pdf") {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
        let fullText = "";
        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            fullText += textContent.items.map(item => item.str).join(" ") + "\n";
        }
        extractedText = fullText;
        displayContent(file.name);
    } else {
        const reader = new FileReader();
        reader.onload = (event) => {
            extractedText = event.target.result;
            displayContent(file.name);
        };
        reader.readAsText(file);
    }
});

analyzeBtn.addEventListener('click', async () => {
    if (!extractedText) {
        alert("Please upload a file first!");
        return;
    }

    analyzeBtn.innerText = "Analyzing...";
    analyzeBtn.disabled = true;

    try {
        console.log("Sending request to backend...");
        console.log("Text length:", extractedText.length);
        console.log("First 200 chars:", extractedText.substring(0, 200));

        const response = await fetch('http://localhost:8001/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: extractedText })
        });

        console.log(" Response status:", response.status);

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Server error:", errorText);
            throw new Error(`Server error: ${response.status} - ${errorText}`);
        }

        const data = await response.json();

        console.log("Received data:");
        console.log(JSON.stringify(data, null, 2));

        renderAnalysis(data);

    } catch (error) {
        console.error("Full error:", error);
        alert(`Analysis failed: ${error.message}\n\nCheck browser console (F12) for details.`);

    } finally {
        analyzeBtn.innerText = "Analyze transcript";
        analyzeBtn.disabled = false;
    }
});

function renderAnalysis(data) {
    console.log("Rendering analysis...", data);

    // Validate data structure
    if (!data || !data.consensus || !data.detailed_analysis) {
        console.error("Invalid data structure:", data);
        analysisResult.innerHTML = `
            <div style="background: #7f1d1d; padding: 20px; border-radius: 8px; border-left: 5px solid #dc2626;">
                <h2 style="color: #fca5a5;">Error: Invalid response structure</h2>
                <pre style="background: #1e293b; padding: 10px; overflow: auto; border-radius: 4px;">${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
        return;
    }

    const consensus = data.consensus;
    const revenue = data.detailed_analysis.revenue || {};
    const profitability = data.detailed_analysis.profitability || {};
    const management = data.detailed_analysis.management || {};

    analysisResult.innerHTML = `
        <div style="background: #1e293b; padding: 25px; border-radius: 12px; border-left: 5px solid #3b82f6; margin-top: 20px;">
            <h2 style="color: #60a5fa; margin-top: 0; font-size: 1.8rem;">
                Overall Score: ${consensus.overall_score || 'N/A'}/10
            </h2>
            
            <div style="background: rgba(59, 130, 246, 0.1); padding: 15px; border-radius: 8px; margin: 15px 0;">
                <p style="margin: 5px 0;"><strong style="color: #93c5fd;">Verdict:</strong> ${consensus.verdict || 'N/A'}</p>
                <p style="margin: 5px 0;"><strong style="color: #93c5fd;">Confidence:</strong> ${consensus.confidence || 'N/A'}</p>
                <p style="margin: 5px 0;"><strong style="color: #93c5fd;">Recommendation:</strong> ${consensus.recommendation || 'N/A'}</p>
            </div>
            
            <hr style="border: 0; border-top: 1px solid #334155; margin: 25px 0;">
            
            <h3 style="color: #60a5fa; margin-bottom: 15px;">Agent Breakdown</h3>
            
            <div style="display: grid; gap: 15px;">
                ${renderAgentCard('💰 Revenue', revenue)}
                ${renderAgentCard('📈 Profitability', profitability)}
                ${renderAgentCard('👔 Management', management)}
            </div>
            
            ${renderDetailedInsights(data.detailed_analysis)}
            
            ${renderRedFlags(consensus.red_flags)}
        </div>
    `;
}

function renderAgentCard(title, agentData) {
    const score = agentData.score || 'N/A';
    const verdict = agentData.verdict || 'N/A';
    const scoreColor = score >= 7 ? '#4ade80' : score >= 5 ? '#fbbf24' : '#fb7185';

    return `
        <div style="background: rgba(30, 41, 59, 0.6); padding: 15px; border-radius: 8px; border-left: 3px solid ${scoreColor};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <strong style="color: #e2e8f0; font-size: 1.1rem;">${title}</strong>
                <span style="color: ${scoreColor}; font-weight: 600; font-size: 1.2rem;">
                    ${score}/10
                </span>
            </div>
            <div style="color: #94a3b8; margin-top: 5px;">
                ${verdict}
            </div>
        </div>
    `;
}

function renderDetailedInsights(analysis) {
    if (!analysis) return '';

    let html = '<hr style="border: 0; border-top: 1px solid #334155; margin: 25px 0;">';
    html += '<h3 style="color: #60a5fa; margin-bottom: 15px;">💡 Key Insights</h3>';
    html += '<div style="display: grid; gap: 15px;">';

    // Revenue highlights
    if (analysis.revenue?.highlights && analysis.revenue.highlights.length > 0) {
        html += '<div style="background: rgba(34, 197, 94, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #22c55e;">';
        html += '<strong style="color: #4ade80; display: block; margin-bottom: 10px;">✓ Revenue Highlights</strong>';
        html += '<ul style="margin: 5px 0; padding-left: 20px; color: #cbd5e1;">';
        analysis.revenue.highlights.slice(0, 3).forEach(h => {
            html += `<li style="margin: 5px 0;">${h}</li>`;
        });
        html += '</ul></div>';
    }

    // Profitability concerns
    if (analysis.profitability?.concerns && analysis.profitability.concerns.length > 0) {
        html += '<div style="background: rgba(251, 113, 133, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #fb7185;">';
        html += '<strong style="color: #fb7185; display: block; margin-bottom: 10px;">⚠️ Profitability Concerns</strong>';
        html += '<ul style="margin: 5px 0; padding-left: 20px; color: #cbd5e1;">';
        analysis.profitability.concerns.slice(0, 2).forEach(c => {
            html += `<li style="margin: 5px 0;">${c}</li>`;
        });
        html += '</ul></div>';
    }

    // Management signals
    if (analysis.management?.positive_signals && analysis.management.positive_signals.length > 0) {
        html += '<div style="background: rgba(96, 165, 250, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #60a5fa;">';
        html += '<strong style="color: #60a5fa; display: block; margin-bottom: 10px;">📢 Management Signals</strong>';
        html += '<ul style="margin: 5px 0; padding-left: 20px; color: #cbd5e1;">';
        analysis.management.positive_signals.slice(0, 3).forEach(s => {
            html += `<li style="margin: 5px 0;">${s}</li>`;
        });
        html += '</ul></div>';
    }

    html += '</div>';
    return html;
}

function renderRedFlags(redFlags) {
    if (!redFlags || redFlags.length === 0 || (redFlags.length === 1 && redFlags[0] === 'None detected')) {
        return `
            <hr style="border: 0; border-top: 1px solid #334155; margin: 25px 0;">
            <div style="background: rgba(34, 197, 94, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #22c55e;">
                <strong style="color: #4ade80;">✓ No Red Flags Detected</strong>
            </div>
        `;
    }

    let html = '<hr style="border: 0; border-top: 1px solid #334155; margin: 25px 0;">';
    html += '<div style="background: rgba(251, 113, 133, 0.1); padding: 15px; border-radius: 8px; border-left: 3px solid #fb7185;">';
    html += '<strong style="color: #fb7185; display: block; margin-bottom: 10px;">🚩 Red Flags</strong>';
    html += '<ul style="margin: 5px 0; padding-left: 20px; color: #cbd5e1;">';
    redFlags.forEach(flag => {
        html += `<li style="margin: 5px 0;">${flag}</li>`;
    });
    html += '</ul></div>';

    return html;
}

function displayContent(fileName) {
    fileDisplayArea.innerHTML = `
        <div style="background: rgba(34, 197, 94, 0.1); padding: 12px; border-radius: 6px; border: 1px solid #22c55e;">
            <p style="color: #4ade80; margin: 0;"> Loaded: ${fileName}</p>
        </div>
    `;
}