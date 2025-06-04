def rank_projects(project_texts):
    tokenizer = BertTokenizer.from_pretrained('best_ranking_tf')
    model = TFBertForSequenceClassification.from_pretrained('best_ranking_tf')
    tokens = tokenizer(project_texts, padding=True, truncation=True, return_tensors='tf', max_length=256)
    outputs = model(tokens)
    probs = tf.nn.softmax(outputs.logits, axis=1)
    scores = tf.reduce_max(probs, axis=1).numpy()
    return sorted(zip(project_texts, scores), key=lambda x: x[1], reverse=True)

    if __name__ == "__main__":
        project_texts = [
            "Project on AI for healthcare",
            "Research on renewable energy",
            "Study of quantum computing applications"
        ]
        ranked_projects = rank_projects(project_texts)
        for project, score in ranked_projects:
            print(f"Project: {project}, Score: {score}")