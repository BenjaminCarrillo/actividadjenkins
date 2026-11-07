from flask import Flask, request

app = Flask(__name__)

@app.route('/hello')
def hello():
    """
    Endpoint para saludar al usuario.

    Parámetros:
    name (str): Nombre del usuario.

    Retorna:
    str: Mensaje de saludo.
    """
    name = request.args.get('name')
    return f"Hello, {name}!"

if __name__ == '__main__':
    app.run(debug=True)