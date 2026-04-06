from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def test():
    limit = request.args.get('limit', 200, type=int)
    return str(limit)

if __name__ == '__main__':
    with app.test_request_context('/?limit=50'):
        print(test())
