from flask import Flask, request, jsonify
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = "1m2Z5i55RHsYsi2f3PNhYQgZYBolfgfD3bzhNWbD_-LM"
SAMPLE_RANGE_NAME = "Sheet1!A1"


def readText():
    items = []
    with open('test.txt', 'r') as f:
        lines = f.readlines()
        for item in lines:
            items.append([item.replace('\n', '')])
    return items


def authenticate_google_sheets():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=3000)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def append_to_google_sheets(data):
    creds = authenticate_google_sheets()
    try:
        service = build("sheets", "v4", credentials=creds)
        valueData = [data]  # Assuming data is a single item list
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .append(spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
                    valueInputOption="USER_ENTERED", body={"values": valueData})
            .execute()
        )
        return result
    except HttpError as err:
        return str(err)


@app.route('/append_data', methods=['POST'])
def append_data():
    try:
        data = request.json['data']  # Assuming frontend sends data in JSON format
        result = append_to_google_sheets(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/', methods=['GET'])
def index():
    return jsonify({'hello':'hello'})

if __name__ == "__main__":
    app.run(debug=True)
