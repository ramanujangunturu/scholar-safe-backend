from transformers import TFBertForSequenceClassification, BertTokenizer
import tensorflow as tf

model_path = "/home/ramanujangunturu/Workspace/mini-proj/scholarSafe/ScholarSafeBackend/best_ranking_tf"

# Load tokenizer and model
tokenizer = BertTokenizer.from_pretrained(model_path)
model = TFBertForSequenceClassification.from_pretrained(model_path)

print("Model and tokenizer loaded successfully")

# List of project ideas
texts = [
    "AI chatbot for healthcare appointment booking",
    "Blockchain-based voting system",
    "Climate prediction using satellite data",
    "Smart home energy management system",
    "Personalized learning platform with AI tutors",
    "Real-time sign language translator",
    "Automated code review tool using NLP",
    "Crowdsourced disaster response app",
    "AI-powered job recommendation engine",
    "Augmented reality navigation app for indoor spaces"
]

# Tokenize input
tokens = tokenizer(texts, padding=True, truncation=True, return_tensors="tf", max_length=256)

# Forward pass
outputs = model(tokens)

# Apply softmax to get probabilities
probs = tf.nn.softmax(outputs.logits, axis=1)

# Define rank values according to your label encoding (example: 1 to 5)
rank_values = tf.constant([1, 2, 3, 4, 5], dtype=tf.float32)

# Calculate expected rank (weighted sum)
expected_ranks = tf.reduce_sum(probs * rank_values, axis=1).numpy()

# Sort projects by expected rank (lower is better)
projects_sorted = sorted(zip(texts, expected_ranks), key=lambda x: x[1])

# Assign integer ranks (1 is best)
integer_ranks = {proj: rank+1 for rank, (proj, _) in enumerate(projects_sorted)}

print("\n📊 Ranked Projects with Integer Ranks:\n")
for proj in texts:
    print(f"Rank {integer_ranks[proj]}: {proj}")
