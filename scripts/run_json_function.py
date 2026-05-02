import json
from src.ai_json_function import analyze_text_to_validated_json
 
text = "Subject: Urgent password reset required. Click http://fake-link.example now."
result = analyze_text_to_validated_json(text)
 
print(json.dumps(result, indent=2))

