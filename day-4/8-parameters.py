# What is a parameter in an LLM?
# Parameters are the weights and biases
# that a model learns during training.
# They determine how the model processes input data and generates output.
# The number of parameters in a model is often used as a measure
# of its complexity and capacity to learn from data.
# Generally, larger models with more parameters can capture
# more complex patterns in data, but they also require
# more computational resources to train and use.


# For example, BERT has 110 million parameters, while GPT-3 has 175 billion parameters.
# parameters in simple words are like the knobs and dials that a model can adjust to learn from data.
# x = input
# w = weights (parameters)
# b = bias (parameters)
# y = output

from transformers import AutoModel

def count_parameters(model):
    model = AutoModel.from_pretrained(model)
    total = sum(
        p.numel()
        for p in model.parameters()
    )

    print(f"{model}: {total:,} parameters")

count_parameters("bert-base-uncased")
count_parameters("distilbert-base-uncased")
count_parameters("gpt2")
