import yfinance as yf
import pandas as pd
from pmdarima.arima import auto_arima
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
#завантаження даних
gs = yf.download("GS", start="2015-01-01", end="2022-01-01")
dataset = gs.copy()
dataset = dataset.reset_index()
dataset['Date'] = pd.to_datetime(dataset['Date'])
dataset.set_index('Date', inplace=True)
dataset = dataset['Close'].to_frame()
model = auto_arima(dataset['Close'], seasonal=False, trace=True)
def arima_forecast(history):
model = ARIMA(history, order=(0,1,0))
model_fit = model.fit()
output = model_fit.forecast()
yhat = output[0]
return yhat
X = dataset.values
size = int(len(X) * 0.8)
train, test = X[0:size], X[size:len(X)]
history = [x for x in train]
predictions = list()
for t in range(len(test)):
yhat = arima_forecast(history)
predictions.append(yhat)
obs = test[t]
history.append(obs)
plt.figure(figsize=(12, 6), dpi=100)
plt.plot(dataset.iloc[size:,:].index, test, label='Real')
plt.plot(dataset.iloc[size:,:].index, predictions, color='red', label='Predicted')
plt.title('ARIMA Predictions / Actual Values')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.show()
