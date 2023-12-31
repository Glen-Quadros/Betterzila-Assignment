# -*- coding: utf-8 -*-
"""Betterzilla.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bvuL2bg7eatoO7z1ZPoXtJ08e7IzaUts

Installing the necessary dependencies
"""

!pip install ktrain

!git clone https://github.com/laxmimerit/IMDB-Movie-Reviews-Large-Dataset-50k.git

"""Importing the libraries"""

import numpy as np
import pandas as pd
import tensorflow as tf
import ktrain
from ktrain import text

"""Data Preparation:
I've loaded the training and test data from Excel files (train.xlsx and test.xlsx).
The training data contains movie reviews in the ‘Reviews’ column and corresponding sentiment labels in the ‘Sentiment’ column.
"""

data_train = pd.read_excel('/content/IMDB-Movie-Reviews-Large-Dataset-50k/train.xlsx', dtype=str)

data_train

data_test = pd.read_excel('/content/IMDB-Movie-Reviews-Large-Dataset-50k/test.xlsx', dtype=str)

data_test

"""Text Preprocessing:
I've used ktrain to preprocess the text data.
The maximum sequence length for the reviews is set to 500 tokens.
The preprocessing mode is set to ‘bert’.
"""

(X_train, y_train), (X_test, y_test), preprocess = text.texts_from_df(train_df = data_train,
                                                                      text_column = 'Reviews',
                                                                      label_columns = 'Sentiment',
                                                                      val_df = data_test,
                                                                      maxlen = 500,
                                                                      preprocess_mode = 'bert')

X_train[0].shape

"""Model Creation:
I’ve created a sentiment analysis model using the BERT architecture.
The model is named ‘bert’.
It’s trained on the preprocessed training data.
"""

model = text.text_classifier(name = 'bert',
                             train_data = (X_train, y_train),
                             preproc = preprocess)

"""Model Training:
I've used a one-cycle learning rate schedule to train the model.
The learning rate was found using the lr_find() method.
The optimal learning rate was chosen based on the plot of learning rates.
The model was trained for one epoch with a batch size of 6.
"""

learner = ktrain.get_learner(model = model,
                             train_data = (X_train, y_train),
                             val_data = (X_test, y_test),
                             batch_size = 6)

learner.lr_find()
learner.lr.plot()

learner.fit_onecycle(lr = 2e-5, epochs=1)

predictor = ktrain.get_predictor(learner.model, preproc=preprocess)

"""I've saved the midel for furture use"""

predictor.save('/content/bert')

X_test = data_test['Reviews'].tolist()
y_pred = predictor.predict(X_test)

"""Model Evaluation:
I’ve used the trained model to make predictions on the test data.
The predictions were converted to binary labels (1 for positive, 0 for negative).
The confusion matrix was computed to evaluate the model’s performance.
Precision, recall, and F1-score were calculated.
"""

from sklearn.metrics import confusion_matrix

y_pred_binary = [1 if label == 'pos' else 0 for label in y_pred]

cm = confusion_matrix(y_test[:, 1], y_pred_binary)

print("Confusion Matrix:")
print(cm)

from sklearn.metrics import precision_score, recall_score, f1_score

precision = precision_score(y_test[:, 1], y_pred_binary)
recall = recall_score(y_test[:, 1], y_pred_binary)
f1 = f1_score(y_test[:, 1], y_pred_binary)

print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1-Score: {f1:.3f}")

import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

y_pred_binary = [1 if label == 'pos' else 0 for label in y_pred]

fpr, tpr, _ = roc_curve(y_test[:, 1], y_pred_binary)
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='b', lw=2, label=f'AUC = {roc_auc:.2f}')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate (FPR)')
plt.ylabel('True Positive Rate (TPR)')
plt.title('ROC Curve')
plt.legend(loc='lower right')
plt.grid(True)
plt.show()

"""Results:
The confusion matrix provides insights into true positives, true negatives, false positives, and false negatives.
Recall (sensitivity) measures the proportion of actual positive cases correctly predicted by the model.
F1-score balances precision and recall.
"""

