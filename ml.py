from sklearn import model_selection
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from os import path
import pandas

def alg_maker(alg):
    return alg()
algorithm = GaussianNB

dataset = pandas.read_csv("gender_age_dataset.csv")
dataset = dataset.fillna(0)
array = dataset.values

category_percentages = pandas.read_csv(path.join("Output", "category_percentage.csv"))
percentages = [list((category_percentages.values.tolist())[0][1:])]
#print(percentages)

X = array[:, 2:-1]
Y = array[:, 0]
validation_size = 0.20
seed = 7
X_train, X_validation, Y_train, Y_validation = model_selection.train_test_split(X, Y, test_size=validation_size, random_state=seed)
#print("Train:",X_train,Y_train)
#print("Valid:",X_validation,Y_validation)
alg = alg_maker(algorithm)#GaussianNB()#SVC(gamma="auto")
alg.fit(X_train,Y_train)
predictions = alg.predict(X_validation)
print("Accuracy:",accuracy_score(Y_validation, predictions)*100,"%")
print("Errors made:",confusion_matrix(Y_validation, predictions))
#print(classification_report(Y_validation, predictions))

alg = alg_maker(algorithm)
alg.fit(X,Y)
predictions_for_history_gender = alg.predict(percentages)
print("Predicted gender:",predictions_for_history_gender)
#print("Accuracy:",accuracy_score(["M"], predictions_for_history_gender)*100,"%")
#print("Errors made:",confusion_matrix(["M"], predictions_for_history_gender))
#print(classification_report(["M"], predictions_for_history_gender))

X_age = array[:, 2:-1]
Y_age = array[:, 1]
Y_age=Y_age.astype('int')
validation_size = 0.50
seed = 7
X_age_train, X_age_validation, Y_age_train, Y_age_validation = model_selection.train_test_split(X_age, Y_age, test_size=validation_size, random_state=seed)
#print("Train (for Age):",X_age_train,Y_age_train)
#print("Valid (for Age):",X_age_validation,Y_age_validation)
alg_age = alg_maker(algorithm)#SVC(gamma="auto")
alg_age.fit(X_age_train,Y_age_train)
predictions = alg_age.predict(X_age_validation)
print("Accuracy:",accuracy_score(Y_age_validation, predictions)*100,"%")
print("Errors made:",confusion_matrix(Y_age_validation, predictions))
#print(classification_report(Y_age_validation, predictions))

alg_age = alg_maker(algorithm)#SVC(gamma="auto")
alg_age.fit(X_age,Y_age)
predictions_for_history_age = alg_age.predict(percentages)
print("Predicted Age:",predictions_for_history_age)