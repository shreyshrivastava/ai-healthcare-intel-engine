# Healthcare Intelligence Engine

![Healthcare Intelligence Engine routing symptoms to Cardiology, flagging a high-risk report, and catching a warfarin and aspirin interaction](docs/demo.gif)

Describe a patient's symptoms, paste a clinical report, or list their medications. The app tells you what it makes of them and why.

[Try the live demo](https://healthcare-intel-engine-shrey.streamlit.app/)

This is a portfolio project that runs on synthetic data. It isn't a medical device, and nothing it says is medical advice.

## What it does

### Symptom routing

Write the symptoms in plain language and the app suggests which specialty fits best, with any others that came close. If the description doesn't match anything it knows, it says there's no clear match.

### Second-opinion risk

Paste a de-identified diagnosis summary. You get a Low, Medium or High rating, whether a second opinion is recommended, and the exact phrases behind the rating, so "septic shock" and "vasopressors" are right there next to the verdict.

### Drug interactions

List two or more drugs. Each known interaction comes back with its severity and the reason for it, along with an overall risk for the whole list. Common alternative names work too.

## Try it

Every tool has sample inputs you can load with one click, so you don't need to come up with a case of your own.

## Run it yourself

```bash
pip install -r requirements.txt
streamlit run ai-healthcare-intel-engine/frontend/app.py
```

## Limits

The drug graph is a small demo set, and the risk rating comes from fixed rules. Neither should be used on a real patient.
