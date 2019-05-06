from app import app
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB, BernoulliNB, MultinomialNB


from flask import Flask, render_template, request
# from werkzeug import secure_filename


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/bayseian')
def bayseianClassifier():
    data = pd.read_csv("app/oasis_longitudinal.csv")  # Replace # with path of Dataset
    print(data.head())
    # Convert categorical variable to numeric
    data["M/F_C"]=np.where(data["M/F"]=="M",0,1)
    data["Group_C"]=np.where(data["Group"]=="Demented",0,1)
    # Cleaning dataset of NaN
    data=data[['M/F_C', 'Age', 'EDUC', 'SES', 'MMSE', 'eTIV', 'nWBV', 'ASF', 'Group_C']].dropna(axis=0, how='any')


    # Split dataset in training and test datasets
    X_train, X_test = train_test_split(data, test_size=0.5, random_state=int(time.time()))



    gnb = GaussianNB()
    used_features =['M/F_C', 'Age', 'EDUC', 'SES', 'MMSE', 'eTIV', 'nWBV', 'ASF']

    # Train classifier
    gnb.fit(
        X_train[used_features].values,
        X_train["Group_C"]
    )
    y_pred = gnb.predict(X_test[used_features])
    
    tableData = []
    print (len(y_pred), len(X_train))
    i=0
    for index, row in X_test.iterrows():
        dic = dict(row)
        # print(row[0])
        dic["Group"] = "Affected" if dic["Group_C"] else "Not Affected"
        dic["Prediction"]= "Affected" if y_pred[i] else "Not Affected"
        dic["Gender"] = "Male" if dic["M/F_C"] else "Female"
        dic["green"] = True if (dic['Group'] == dic["Prediction"]) else False
        print(dic["green"])
        i=i+1
        tableData.append(dic)
       
    # for i in range(len(y_pred)):
    #     print[]
    # Print results
    return render_template("table.html", data = tableData, green = dic["green"])

    return("Number of mislabeled points out of a total {} points : {}, performance {:05.2f}% ==> Naive Bayes, "
        .format(
            X_test.shape[0],
            (X_test["Group_C"] != y_pred).sum(),
            100*(1-(X_test["Group_C"] != y_pred).sum()/X_test.shape[0])
    ))



@app.route('/svm')
def svm():

    sns.set()

    df = pd.read_csv("oasis_longitudinal.csv")
    df.head()

    df = df.loc[df['Visit']==1]
    df = df.reset_index(drop=True) 
    df['M/F'] = df['M/F'].replace(['F','M'], [0,1])
    df['Group'] = df['Group'].replace(['Converted'], ['Demented']) 
    df['Group'] = df['Group'].replace(['Demented', 'Nondemented'], [1,0]) 
    df = df.drop(['MRI ID', 'Visit', 'Hand'], axis=1)

    pd.isnull(df).sum() 

    df_dropna = df.dropna(axis=0, how='any')
    pd.isnull(df_dropna).sum()

    df_dropna['Group'].value_counts()

    # Draw scatter plot between EDUC and SES
    x = df['EDUC']
    y = df['SES']

    ses_not_null_index = y[~y.isnull()].index
    x = x[ses_not_null_index]
    y = y[ses_not_null_index]

    # Draw trend line in red
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    plt.plot(x, y, 'go', x, p(x), "r--")
    plt.xlabel('Education Level(EDUC)')
    plt.ylabel('Social Economic Status(SES)')

    #plt.show()

    df.groupby(['EDUC'])['SES'].median()

    df["SES"].fillna(df.groupby("EDUC")["SES"].transform("median"), inplace=True)

    pd.isnull(df['SES']).value_counts()
    from sklearn.model_selection import train_test_split
    from sklearn import preprocessing
    from sklearn.preprocessing import MinMaxScaler 
    from sklearn.model_selection import cross_val_score
    Y = df['Group']
    X = df[['M/F', 'Age', 'EDUC', 'SES', 'MMSE', 'eTIV', 'nWBV', 'ASF']] # Features we use

    # splitting into three sets
    X_trainval, X_test, Y_trainval, Y_test = train_test_split(
    X, Y, random_state=0)

    # Feature scaling
    scaler = MinMaxScaler().fit(X_trainval)
    X_trainval_scaled = scaler.transform(X_trainval)
    X_test_scaled = scaler.transform(X_test)

    # Dataset after dropping missing value rows
    Y = df_dropna['Group'].values # Target for the model
    X = df_dropna[['M/F', 'Age', 'EDUC', 'SES', 'MMSE', 'eTIV', 'nWBV', 'ASF']] # Features we use

    # splitting into three sets
    X_trainval_dna, X_test_dna, Y_trainval_dna, Y_test_dna = train_test_split(
    X, Y, random_state=0)

    # Feature scaling
    scaler = MinMaxScaler().fit(X_trainval_dna)
    X_trainval_scaled_dna = scaler.transform(X_trainval_dna)
    X_test_scaled_dna = scaler.transform(X_test_dna)

    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, roc_curve, auc

    best_score = 0
    kfolds=5
    acc=[]
    for c_paramter in [0.001, 0.01, 0.1, 1, 10, 100, 1000]: #iterate over the values we need to try for the parameter C
        for gamma_paramter in [0.001, 0.01, 0.1, 1, 10, 100, 1000]:
            for k_parameter in ['rbf', 'linear', 'poly', 'sigmoid']:
                svmModel = SVC(kernel=k_parameter, C=c_paramter, gamma=gamma_paramter) #define the model
                # perform cross-validation
                scores = cross_val_score(svmModel, X_trainval_scaled, Y_trainval, cv=kfolds, scoring='accuracy')
                # the training set will be split internally into training and cross validation

                # compute mean cross-validation accuracy
                score = np.mean(scores)
                # if we got a better score, store the score and parameters
                if score > best_score:
                    best_score = score #store the score 
                    best_parameter_c = c_paramter #store the parameter c
                    best_parameter_gamma = gamma_paramter # store the parameter gamma
                    best_parameter_k = k_parameter
                

    # rebuild a model with best parameters to get score 
    SelectedSVMmodel = SVC(C=best_parameter_c, gamma=best_parameter_gamma, kernel=best_parameter_k).fit(X_trainval_scaled, Y_trainval)

    test_score = SelectedSVMmodel.score(X_test_scaled, Y_test)
    PredictedOutput = SelectedSVMmodel.predict(X_test_scaled)
    print(PredictedOutput)
    test_recall = recall_score(Y_test, PredictedOutput, pos_label=1)
    fpr, tpr, thresholds = roc_curve(Y_test, PredictedOutput, pos_label=1)
    test_auc = auc(fpr, tpr)
    print("Best accuracy on cross validation set is:", best_score)
    print("Best parameter for c is: ", best_parameter_c)
    print("Best parameter for gamma is: ", best_parameter_gamma)
    print("Best parameter for kernel is: ", best_parameter_k)
    print("Test accuracy with the best parameters is", test_score)
    print("Test recall with the best parameters is", test_recall)
    print("Test recall with the best parameter is", test_auc)

    m = 'SVM'
    acc.append([m, test_score, test_recall, test_auc, fpr, tpr, thresholds])






@app.route('/table', methods = ['GET', 'POST'])
def showTab():
    return render_template("table.html")



	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename)
        return 'file uploaded successfully'+f.filename
    #return render_template('upload.html')

@app.route('/cat', methods = ['GET', 'POST'])
def showCat():
    return render_template("category.html")