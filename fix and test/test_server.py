#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <html>
    <head>
        <title>Readloom Test Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }
            h1 {
                color: #333;
            }
            .success {
                color: green;
                font-weight: bold;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Readloom Test Server</h1>
            <p class="success">✅ If you can see this page, the Flask server is running correctly!</p>
            <p>This is a simple test server to verify that the Docker container's networking is set up correctly.</p>
            <p>You should now be able to access the main Readloom application.</p>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting test server on 0.0.0.0:7227...")
    app.run(host='0.0.0.0', port=7227, debug=True)
