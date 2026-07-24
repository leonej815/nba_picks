import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from pathlib import Path
import sys
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from include.db import DB

def create_model():
    # query all records from the database into a dataframe
    db_path = Path(__file__).resolve().parent.parent/'sqlite'/'data.sqlite'
    db = DB(db_path)
    df = db.select_all_to_df()

    # define features
    features = ['home_offrtg', 'home_defrtg', 'away_offrtg', 'away_defrtg', 'home_spread', 'home_pie', 'away_pie']
    X = df[features]

    # create margin and home_cover and define target
    df['margin'] = df['home_score'] - df['away_score']
    df['home_cover'] = (df['margin'] + df['home_spread'] > 0).astype(int)
    y = df["home_cover"]

    # split into test and training groups
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    
    # use a Pipeline to scale features automatically before passing them to LogisticRegression
    model = make_pipeline(
        StandardScaler(), 
        LogisticRegression(max_iter=1000, random_state=42)
    )

    # train_model
    model.fit(X_train, y_train)

    # predict on the test set
    predictions = model.predict(X_test)

    # calculate and print success rate
    success_rate = accuracy_score(y_test, predictions)
    print(f"Model Success Rate (Accuracy): {success_rate:.2%}")

    # thresholds for confidence level test
    thresholds = [0.55, 0.6, 0.65, 0.7]

    # loop through thresholds and test the model at each
    for threshold in thresholds:

        # gets the probabilities for each outcome for each test game
        probs = model.predict_proba(X_test)
        
        # check if the model's confidence for either class (0 or 1) is >= threshold
        # probs[:, 1] is the probability of class 1, probs[:, 0] is the probability of class 0
        confident_mask = (probs[:, 1] >= threshold) | (probs[:, 0] >= threshold)
        
        # get the subset of test inputs where the predicted outcome met the threshold
        X_confident = X_test[confident_mask]
        y_confident = y_test[confident_mask]
        
        # use the subset of test inputs that met the threshold to test the model
        if len(X_confident) > 0:
            confident_preds = model.predict(X_confident)
            confident_accuracy = accuracy_score(y_confident, confident_preds)
            print(f"\nAccuracy at {threshold:.0%} confidence: {confident_accuracy:.2%}")
            print(f"Count of confident games: {len(X_confident)} out of {len(X_test)}")
        else:
            print(f"No games met the {threshold:.0%} confidence threshold.")

    # create model directory if it doesn't exist
    directory_path = Path(__file__).parent.parent/'model'
    directory_path.mkdir(parents=True, exist_ok=True)

    # export model
    joblib.dump(model, "model/nba_spread_model.joblib")
    joblib.dump(features, "model/nba_spread_features.joblib")
    print('\nModel trained and exported as "nba_spread_model.joblib" and features as "nba_features.joblib"')

if __name__ == "__main__":
    create_model()