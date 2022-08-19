import joblib
'''
Joblib is a set of tools to provide lightweight pipelining in Python
    1. transparent disk-caching of functions and lazy re-evaluation (memoize pattern)
    2. easy simple parallel computing
'''
import pandas as pd

class RandomForestClassifier:
    def __init__(self):
        path_to_artifacts = "../../research/"
        self.values_fill_missing =  joblib.load(path_to_artifacts + "train_mode.joblib")
        self.encoders = joblib.load(path_to_artifacts + "encoders.joblib")
        self.model = joblib.load(path_to_artifacts + "random_forest.joblib")

    def preprocessing(self, input_data):
        # JSON to pandas DataFrame
        input_data = pd.DataFrame(input_data, index=[0])
        # fill missing values
        input_data.fillna(self.values_fill_missing)
        # convert categoricals
        for column in [
            "workclass",
            "education",
            "marital-status",
            "occupation",
            "relationship",
            "race",
            "sex",
            "native-country",
        ]:
            categorical_convert = self.encoders[column]
            input_data[column] = categorical_convert.transform(input_data[column])

        return input_data

    def predict(self, input_data):
        return self.model.predict_proba(input_data)

    def postprocessing(self, input_data):
        '''
        Converts the probabilities into values. 
        If the probability is greater than or equal to 50k, set label to >=50k.
        If probability is less than 50k, set label to <50k
        '''
        
        label = "<=50K"
        if input_data[1] > 0.5:
            label = ">50K"
        return {"probability": input_data[1], "label": label, "status": "OK"}

    def compute_prediction(self, input_data):
        try:
            # Process the raw data
            input_data = self.preprocessing(input_data)
            
            # Predict one sample
            prediction = self.predict(input_data)[0]  # only one sample
            
            # Postprocess the prediction
            prediction = self.postprocessing(prediction)
        
        except Exception as e:
            return {"status": "Error", "message": str(e)}

        return prediction