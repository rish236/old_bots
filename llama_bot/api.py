from flask import Flask, jsonify, request
import csv
import os

app = Flask(__name__)
@app.route('/wallet_checker/<address>', methods=['GET'])
def wallet_checker(address):
    token_data = []
    directory = 'tokens'
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                token_name = filename[:-4] 
                with open(os.path.join(directory, filename), mode='r') as csv_file:
                    reader = csv.DictReader(csv_file)
                    column_names = next(reader)
                    column_names_lower = [name.lower() for name in column_names]
                    for row in reader:
                        print(row)
                        if row['wallet'] == address:
                            token_data.append({
                                'tokenName': token_name,
                                'sentAmount': row['SentAmount']
                            })
    
    except:
        pass
    return jsonify(token_data)

if __name__ == '__main__':
    app.run(debug=True)
