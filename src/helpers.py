import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import tensorflow.keras as keras

from os.path import exists
from typing import Optional
from tensorflow.keras.layers import Dense, Dropout

class Path:
  def plots(self, path: Optional[str]):
    return self.storage(f'plots/{path}')

  def logs(self, path: Optional[str]):    
    return self.storage(f'logs/{path}')

  def storage(self, path: Optional[str]):    
    path = self.clean_path(path) 

    return f'storage{path}'

  def resources(self, path: Optional[str]):    
    path = self.clean_path(path) 

    return f'resources{path}'

  def clean_path(self, path: Optional[str]):
    if path is None:
      return ''

    if path.endswith('/') is True:
      path = path[:-1]

    if path.startswith('/') is True:
      return path 

    return f'/{path}'

path = Path()

def load_model():
  model_exists = exists('storage/lending-model.keras')

  if (model_exists):
    return keras.models.load_model('storage/lending-model.keras')

  model = keras.models.Sequential()

  # First neuron layer is good to match the shape of X_train.
  # `X_train.shape = (316175, 78)`:
  model.add(keras.layers.Dense(78, activation='relu'))
  model.add(keras.layers.Dropout(0.2))

  model.add(keras.layers.Dense(39, activation='relu'))
  model.add(keras.layers.Dropout(0.2))

  model.add(keras.layers.Dense(19, activation='relu'))
  model.add(keras.layers.Dropout(0.2))

  # In binary classifiction problems we want the 
  # last neuron activation to be sigmoid.
  model.add(Dense(1, activation='sigmoid'))

  model.compile(loss='binary_crossentropy', optimizer='adam')

  return model

def get_lending_df(with_plots = True):
  df = pd.read_csv(path.resources('lending.csv')) \
    .drop('emp_title', axis=1) \
    .drop('emp_length', axis=1) \
    .drop('title', axis=1) \
    .drop('grade', axis=1) \
    .drop('issue_d', axis=1)
  
  df['term'] = df['term'].apply(lambda term: int(term[:3]))
  df['earliest_cr_line'] = df['earliest_cr_line'].apply(lambda date: int(date[-4:]))
    
  total_acc_avg = df.groupby('total_acc').mean(numeric_only=True)['mort_acc']
  df['mort_acc'] = df.apply(lambda x: total_acc_avg[x['total_acc']] if np.isnan(x['mort_acc']) else x['mort_acc'], axis=1)

  df['home_ownership'] = df['home_ownership'].replace(['NONE', 'ANY'], 'OTHER')
  df['zip_code'] = df['address'].apply(lambda address: address[-5:]) 

  df['loan_repaid'] = df['loan_status'].map({
    'Fully Paid': 1,
    'Charged Off': 0
  }) 
    
  if with_plots is True:
    plot(
      path=path.plots('dataframe/c-loan-status.png'),
      lamb=lambda: sns.countplot(x='loan_status', data=df)
    )

    # Standard loans
    plot(
      path=path.plots('dataframe/h-loan-amnt.png'),
      lamb=lambda: sns.histplot(df['loan_amnt'], kde=False, bins=40)
    )

    plot(
      size=(12,7),
      path=path.plots('dataframe/correlation.png'),
      lamb=lambda: sns.heatmap(data=df.corr(numeric_only=True), annot=True, cmap='viridis') 
    )

    plot(
      path=path.plots('dataframe/corr-installment-loan-amnt.png'),
      lamb=lambda: sns.scatterplot(x='installment', y='loan_amnt', data=df)
    ) 

    plot(
      size=(12,4),
      path=path.plots('dataframe/c-subgrade.png'),
      lamb=lambda: sns.countplot(
        x='sub_grade',
        data=df,
        hue='loan_status',
        order=sorted(df['sub_grade'].unique()),
        palette='coolwarm'
      )
    )

    plot(
      size=(12,4),
      path=path.plots('dataframe/corr-loan-repaid.png'),
      lamb=lambda: sns.barplot(df.corr(numeric_only=True)['loan_repaid'].sort_values().drop('loan_repaid'))
    )

  dummies_columns = [
    'sub_grade',
    'zip_code',
    'home_ownership',
    'verification_status',
    'application_type',
    'initial_list_status',
    'purpose'
  ] 
  dummies = pd.get_dummies(df[dummies_columns], drop_first=True)
  df = pd.concat([df.drop(dummies_columns, axis=1), dummies], axis=1)

  return df \
    .drop('address', axis=1) \
    .drop('loan_status', axis=1) \
    .dropna()

def plot(path: str, lamb, size=(10,8)):
  plt.figure(figsize=size)
  lamb()
  plt.savefig(path)
