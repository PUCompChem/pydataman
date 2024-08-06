from ioutils.meterac.data_access import read_metadata
import matplotlib.pyplot as plt

df_meteo = read_metadata('https://meter.ac/gs/metadata/meteo.csv')
print(df_meteo)

df_nodes = read_metadata('https://meter.ac/gs/metadata/nodes.csv')
print(df_nodes)

df_earth = read_metadata('https://meter.ac/gs/metadata/earth.csv')
print(df_earth)

# test matplotlip install
# Sample data
x = [1, 2, 3, 4, 5]
y = [2, 4, 6, 8, 10]

# Create a simple plot
plt.plot(x, y, label='Linear Function')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')
plt.title('Simple Matplotlib Plot')
plt.legend()
plt.show()

# test libs installation
import numpy as np
from scipy.stats import norm
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Test scipy
data = np.random.normal(size=1000)
mean, std = norm.fit(data)
print(f'Scipy Test: Mean={mean}, Standard Deviation={std}')

# Test scikit-learn
iris = load_iris()
X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f'Scikit-learn Test: Accuracy={accuracy}')
