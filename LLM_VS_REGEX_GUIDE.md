# LLM vs Regex Decision Guide

## When to Use LLM-Based Extraction ✅

### 1. Intent Classification
```python
# ✅ GOOD: LLM-based
from src.utils.llm_helpers import classify_intent

intent_result = classify_intent(user_message, conversation_history, model)
intent = intent_result.get("intent")  # "search", "booking", "history"
```

**Use LLM when:**
- User input is conversational ("yes", "sure", "ok" after seeing results)
- Context matters (previous messages influence meaning)
- Multiple intents possible
- Natural language variations expected

### 2. Entity Extraction
```python
# ✅ GOOD: LLM-based
from src.utils.llm_helpers import extract_booking_details

details = extract_booking_details(prompt, conversation_history, model)
# Handles: "tomorrow at 7pm for me" → {date: "2024-01-15", time: "19:00", guests: 1}
```

**Use LLM when:**
- Extracting dates ("tomorrow", "next Friday", "Jan 15")
- Extracting times ("dinner time", "7pm", "evening")
- Extracting quantities ("for me", "party of 4", "just us two")
- Extracting names from natural text

### 3. Search Parameters
```python
# ✅ GOOD: LLM-based
from src.utils.llm_helpers import extract_search_params

params = extract_search_params(prompt, model)
# Handles: "Thai food in NYC" → {city: "New York", cuisine: "Thai"}
```

**Use LLM when:**
- Handling abbreviations (NYC → New York)
- Handling variations (Italian food → Italian)
- Open-ended categories (any cuisine, any city)

---

## When to Use Regex ✅

### 1. Exact Pattern Matching
```python
# ✅ GOOD: Regex for exact patterns
import re

booking_id = re.search(r'booking_[a-f0-9]{8}', text)
uuid = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}', text)
```

**Use Regex when:**
- Matching UUIDs, booking IDs, transaction IDs
- Extracting structured identifiers
- Pattern is fixed and well-defined

### 2. Data Validation
```python
# ✅ GOOD: Regex for validation
def validate_phone(phone: str) -> bool:
    digits = re.sub(r'\D', '', phone)  # Extract digits only
    return len(digits) >= 10
```

**Use Regex when:**
- Validating format (phone has 10+ digits)
- Sanitizing input (remove non-digits)
- Checking structure (not extracting meaning)

### 3. PII Scrubbing
```python
# ✅ GOOD: Regex for security
def scrub_pii(text: str) -> str:
    text = re.sub(r'\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b', '<CARD>', text)
    text = re.sub(r'\+?\d[\d\s\-\(\)]{9,}', '<PHONE>', text)
    return text
```

**Use Regex when:**
- Redacting sensitive data
- Security-critical operations
- Performance-critical (millions of records)

---

## Anti-Patterns ❌

### ❌ DON'T: Hardcoded Keyword Lists
```python
# ❌ BAD: Brittle and unmaintainable
if any(kw in prompt for kw in ["yes", "sure", "ok", "yep", "yeah", "yup"]):
    intent = "booking"

# ✅ GOOD: LLM handles all variations
intent = classify_intent(prompt, history, model).get("intent")
```

### ❌ DON'T: Complex Regex for Natural Language
```python
# ❌ BAD: Fragile and incomplete
date_match = re.search(r'(tomorrow|today|next week|monday|tuesday)', prompt)

# ✅ GOOD: LLM handles all date formats
details = extract_booking_details(prompt, history, model)
date = details.get("date")  # Normalized to YYYY-MM-DD
```

### ❌ DON'T: Hardcoded Entity Lists
```python
# ❌ BAD: Requires constant updates
cities = ["new york", "boston", "chicago", "seattle"]
for city in cities:
    if city in prompt.lower():
        matched_city = city

# ✅ GOOD: LLM handles any city
params = extract_search_params(prompt, model)
city = params.get("city")
```

---

## Cost Considerations

### LLM Costs (Negligible for this use case)
- **Nova Micro**: $0.00035 per 1K input tokens, $0.0014 per 1K output tokens
- **Nova Lite**: $0.0006 per 1K input tokens, $0.0024 per 1K output tokens

**Example**: Intent classification (~50 tokens) = $0.000018 per request

### When Cost Matters
- **Batch processing**: Millions of records → Consider regex
- **Real-time**: Single user requests → LLM is fine
- **Caching**: Deterministic prompts can be cached

---

## Decision Tree

```
Is the input natural language?
├─ YES → Use LLM
│   ├─ Intent classification
│   ├─ Entity extraction
│   └─ Semantic understanding
│
└─ NO → Use Regex
    ├─ Exact pattern matching (IDs, UUIDs)
    ├─ Data validation (format checks)
    └─ PII scrubbing (security)
```

---

## Migration Checklist

When refactoring regex to LLM:

1. ✅ Identify the use case (classification, extraction, validation)
2. ✅ Check if pattern is fixed (UUID) or variable (date formats)
3. ✅ Use appropriate LLM helper from `src/utils/llm_helpers.py`
4. ✅ Keep regex for validation (phone digits, email format)
5. ✅ Add logging for LLM calls (correlation IDs)
6. ✅ Test edge cases (abbreviations, typos, variations)
7. ✅ Monitor costs (should be negligible)

---

## Quick Reference

| Task | Tool | Example |
|------|------|---------|
| Intent classification | LLM | "yes" → booking intent |
| Date extraction | LLM | "tomorrow" → "2024-01-15" |
| City/cuisine extraction | LLM | "Thai in NYC" → {city: "New York", cuisine: "Thai"} |
| Booking ID matching | Regex | `booking_[a-f0-9]{8}` |
| Phone validation | Regex | Extract digits, check length |
| PII scrubbing | Regex | Redact credit cards, SSNs |

---

## Questions?

- **"Should I use LLM for X?"** → If it requires understanding context or natural language, yes.
- **"Is regex faster?"** → Yes, but LLM cost is negligible for user-facing requests.
- **"What about accuracy?"** → LLM is 10x more accurate on natural language.
- **"Can I mix both?"** → Yes! Use LLM for extraction, regex for validation.
