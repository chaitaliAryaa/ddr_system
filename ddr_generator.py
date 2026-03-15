"""
ddr_generator.py
Uses Groq API (FREE) to generate DDR report.
Get free API key at: console.groq.com
"""

from groq import Groq

SYSTEM_PROMPT = """You are a professional building diagnostics expert who writes clear, structured DDR (Detailed Diagnostic Reports) for clients.

STRICT RULES:
- Do NOT invent facts not present in the documents.
- If information is missing write "Not Available"
- If information conflicts between documents explicitly mention the conflict
- Use simple, client-friendly language
- Avoid unnecessary technical jargon

OUTPUT FORMAT - use these exact section headers:

## 1. Property Issue Summary
[3-5 sentence executive summary]

## 2. Area-wise Observations
### Area: [Area Name]
- Observation: [what was found]
- Source: [Inspection Report / Thermal Report / Both]
[RELEVANT_IMAGE: None]

## 3. Probable Root Cause
[plain language cause analysis per issue]

## 4. Severity Assessment
| Area | Issue | Severity | Reasoning |
|------|-------|----------|-----------|
[CRITICAL / HIGH / MEDIUM / LOW]

## 5. Recommended Actions
[numbered, prioritized list]

## 6. Additional Notes
[safety notes, context]

## 7. Missing or Unclear Information
[list anything missing or write Not Available]
"""


def generate_ddr(inspection_data, thermal_data, api_key, progress_callback=None):
    client = Groq(api_key=api_key)

    if progress_callback:
        progress_callback("Building message...")

    combined_text = f"""=== INSPECTION REPORT ===

{inspection_data['text']}

=== THERMAL REPORT ===

{thermal_data['text']}

---
Now generate the complete DDR report based on both documents above. Follow the exact format specified."""

    if progress_callback:
        progress_callback("Calling Groq API to generate DDR...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": combined_text}
        ],
        max_tokens=4096,
        temperature=0.2,
    )

    ddr_text = response.choices[0].message.content

    if progress_callback:
        progress_callback("DDR generated successfully!")

    return ddr_text
