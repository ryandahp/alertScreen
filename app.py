from flask import Flask, render_template, Response, request
import time
import threading

app = Flask(__name__)
clients = []

#test

def event_stream():
    while True:
        time.sleep(0.5)
        yield f"data: \n\n"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def sse():
    def stream():
        q = queue.Queue()
        clients.append(q)
        try:
            while True:
                yield f"data: {q.get()}\n\n"
        except GeneratorExit:
            clients.remove(q)
    return Response(stream(), mimetype='text/event-stream')

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    # alert_name = data.get("alert_name", "Unknown Alert")
    alert_name = data
    for q in clients:
        q.put(alert_name)
    return "Webhook received", 200

if __name__ == '__main__':
    import queue
    app.run(debug=True, threaded=True, host="0.0.0.0", port=5670)
