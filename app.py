from flask import Flask, render_template, Response, request
import queue

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
    summary = data.get("payload", {}).get("incident", {}).get("title", "Unknown Alert")
    for q in clients:
        q.put(summary)
    return "OK", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
