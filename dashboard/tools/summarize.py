import sys
import json

def summarize(text):
    # Very basic: just returns the first sentence.
    return text.split('.')[0] + '.'

if __name__ == "__main__":
    try:
        # Input from stdin as JSON
        input_data = json.load(sys.stdin)
        text = input_data.get("text", "")
        summary = summarize(text)
        print(json.dumps({"summary": summary}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))