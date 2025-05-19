from flask import Flask, render_template, Response, request
import queue
import logging
# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

app = Flask(__name__)
clients = []

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/events')
def events():
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
    logging.info(f"Received webhook data: {data}")
    event_type = data.get("payload", {}).get("event_type", "")
    if event_type == "triggered":
        incident = data.get("payload", {}).get("incident", {})
        summary = incident.get("title", "Unknown Alert")
        incident_number = incident.get("incident_number", "N/A")
        message = f"#{incident_number} - {summary}"

        for q in clients:
            q.put(message)
    else:
        logging.info(f"Ignored event type: {event_type}")
        
    return "OK", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
