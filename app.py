from flask import Flask, request, jsonify
from firebase_admin import credentials, messaging, initialize_app
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Firebase Admin SDK
cred = credentials.Certificate("camconnect-b8792-firebase-adminsdk-7suiv-c18da508b1.json")
initialize_app(cred)

@app.route('/send_notification', methods=['POST'])
def send_notification():
    try:
        data = request.get_json()
        print("Incoming data:", data)  # Debug incoming data

        # Validate the 'to' field (FCM token) is present
        if 'to' not in data:
            print("Missing 'to' field")
            return jsonify({
                'success': False,
                'error': "'to' field (FCM token) is required."
            }), 400

        # Validate notification and data fields
        if not all(key in data for key in ['notification', 'data']):
            print("Missing 'notification' or 'data' fields")
            return jsonify({
                'success': False,
                'error': "'notification' and 'data' fields are required."
            }), 400

        # Validate the 'notification' fields
        if not all(key in data['notification'] for key in ['title', 'body']):
            print("Missing 'title' or 'body' in notification")
            return jsonify({
                'success': False,
                'error': "'title' and 'body' in 'notification' are required."
            }), 400

        # Validate the 'data' fields
        if not all(key in data['data'] for key in ['type', 'channelName', 'token', 'callerId']):
            print("Missing required fields in 'data'")
            return jsonify({
                'success': False,
                'error': "Missing required fields in 'data'."
            }), 400

        # Prepare the notification payload
        notification = messaging.Notification(
            title=data['notification']['title'],
            body=data['notification']['body']
        )

        # Prepare the data payload
        data_payload = {
            'type': data['data']['type'],
            'videoChannel': data['data']['channelName'],  # Rename to avoid conflict
            'agoraToken': data['data']['token'],  # Agora token
            'callerId': data['data']['callerId']
        }

        # Create the message payload
        message = messaging.Message(
            notification=notification,
            data=data_payload,
            token=data['to']  # FCM token of the target device
        )

        # Send the notification
        response = messaging.send(message)
        print("Message sent successfully with ID:", response)

        return jsonify({'success': True, 'message_id': response}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500
    



@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
