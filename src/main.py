import time
import calendar
import numpy as np
import seaborn as sns

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from helpers import path, plot, load_model, get_lending_df
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard
from sklearn.metrics import confusion_matrix, classification_report

df = get_lending_df()

X = df.drop('loan_repaid', axis=1).values
y = df['loan_repaid'].values

X_train, X_test, y_train, y_test = train_test_split(
  X,
  y,
  test_size=0.2,
  random_state=101
)

scaler = MinMaxScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = load_model()

model.fit(
  x=X_train,
  y=y_train,
  epochs=600,
  batch_size=256,
  validation_data=(X_test, y_test),
  callbacks=[
    EarlyStopping(
      monitor='val_loss',
      mode='min',
      verbose=1,
      patience=5
    ),
    TensorBoard(
      log_dir=path.logs(f'fit-{calendar.timegm(time.gmtime())}'),
      histogram_freq=1,
      write_graph=True,
      write_images=True,
      update_freq='epoch',
      profile_batch=2,
      embeddings_freq=1
    )
  ]
)

plot(
  path.plots('model/is-overfitting-train-test-data.png'), 
  lambda: sns.lineplot(model.history.history)
)

# For binary classification
predictions = model.predict(X_test)
predictions = np.where(predictions > 0.5, 1, 0)
predictions = predictions.flatten()

print()
print('Confusion Matrix:')
print(confusion_matrix(y_test, predictions))
print()
print('Classification Report:')
print(classification_report(y_test, predictions, zero_division=0))

print()
print('Saving the model at', path.storage('lending-model.keras'))
model.save(path.storage('lending-model.keras'))
