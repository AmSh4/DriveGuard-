from flask import Flask, render_template, jsonify, request
import subprocess

app = Flask(__name__)

# Store the subprocess object for later termination
drowsiness_process = None
alarm_triggered = False
user = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main')
def main_page():
    global user
    return render_template('main_page.html', user=user)

@app.route('/learn_more')
def learn_more():
    return render_template('learn_more.html')

@app.route('/start')
def start_detection():
    global drowsiness_process
    global alarm_triggered
    global user

    if user is None:
        return jsonify({"status": "User details not provided"})

    if int(user['age']) < 18:
        return jsonify({"status": "Underage person detected", "message": "You are not eligible to drive"})

    if drowsiness_process is None:
        # Start the drowsiness detection script
        drowsiness_process = subprocess.Popen(['python', 'drowsiness_detection.py'])
        alarm_triggered = False
        return jsonify({"status": "Drowsiness detection started"})
    else:
        return jsonify({"status": "Drowsiness detection already running"})

@app.route('/stop')
def stop_detection():
    global drowsiness_process
    global alarm_triggered
    if drowsiness_process is not None:
        # Stop the drowsiness detection script if it's running
        drowsiness_process.terminate()
        drowsiness_process = None
        alarm_triggered = False
        return jsonify({"status": "Drowsiness detection stopped"})
    else:
        return jsonify({"status": "Drowsiness detection not running"})

@app.route('/alarm_triggered')
def get_alarm_status():
    global alarm_triggered
    return jsonify({"alarm_triggered": alarm_triggered})

@app.route('/set_alarm_triggered')
def set_alarm_triggered():
    global alarm_triggered
    alarm_triggered = True
    return jsonify({"status": "Alarm triggered"})

@app.route('/log')
def log():
    global user
    if user is not None:
        if int(user['age']) < 18:
            warning = "You are not eligible to drive."
        else:
            warning = None
    else:
        warning = None

    return render_template('log.html', user=user, warning=warning)

@app.route('/log_details')
def log_details():
    global user
    return jsonify(user)

@app.route('/set_user', methods=['POST'])
def set_user():
    global user
    user = request.get_json()
    return jsonify({"status": "User details saved successfully"})

if __name__ == '__main__':
    app.run(debug=True)
