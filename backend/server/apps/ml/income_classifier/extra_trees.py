import joblib
import pandas as pd

class ExtraTreesClassifier:
    
    def __init__(self):
        
        # Set the path where the joblibs are 
        path_to_artifacts = "../../research/"
        
        # Get the fill-in function from joblib
        self.values_fill_missing = joblib.load(path_to_artifacts+"train_mode.joblib")

        # Get the label encoder function from joblib
        self.encoders = joblib.load(path_to_artifacts+"encoders.joblib")

        # Get the trained model from joblib
        self.model = joblib.load(path_to_artifacts+"extra_trees.joblib")
    
    def preprocessing(self, input_data):
        
        input_data = pd.DataFrame(input_data, index=[0])

        # Fill in missing values with the same method as training
        input_data.fillna(self.values_fill_missing)

        # Convert categoricals using label encoding
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
 
        # Return the probability of class
        return self.model.predict_proba(input_data)
    
    def postprocessing(self, input_data):
        
        # Setting a default label
        label = "<=50K"

        # If the probability is greater than 50% than switch label
        if input_data[1] > 0.5:
            label = ">50K"

        # Return dictionary with probability, label, and status
        return {"probability":input_data[1], "label":label, "status":"OK"}
    
    def compute_prediction(self, input_data):
        try:
            
            input_data = self.preprocessing(input_data)
            prediction = self.predict(input_data)[0]
            prediction = self.postprocessing(prediction)
        
        except Exception as e:
            return {"status":"Error", "message":str(e)}

        return prediction
    
