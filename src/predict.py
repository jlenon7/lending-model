import numpy as np

from helpers import load_model, get_lending_df
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

df = get_lending_df(with_plots=False)

model = load_model()

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

customer = df.sample()
scaled_customer = scaler.transform(customer.drop('loan_repaid', axis=1).values.reshape(1, 78))

# For binary classification
prediction = model.predict(scaled_customer)
prediction = np.where(prediction > 0.5, 1, 0)

print()
print('Exam result:          ', customer['loan_repaid'].iloc[0])
print('Exam predicted result:', prediction[0][0])
