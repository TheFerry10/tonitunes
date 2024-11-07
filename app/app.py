from flask import Flask, render_template
import pandas as pd
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
# Sample dropdown options
dropdown_options = ["Option 1", "Option 2", "Option 3"]


@app.route("/")
def index():
    # Load CSV data into a DataFrame
    df = pd.read_csv("data.csv")
    # Convert DataFrame to dictionary to pass it to the template
    table_data = df.to_dict(orient="records")
    return render_template(
        "table.html", table_data=table_data, dropdown_options=dropdown_options
    )


if __name__ == "__main__":
    app.run(host="localhost", debug=True)
