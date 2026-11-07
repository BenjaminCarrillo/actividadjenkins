from app import app


def test_hello_con_nombre():
    cliente = app.test_client()
    respuesta = cliente.get('/hello?name=Ben')
    assert respuesta.status_code == 200
    assert respuesta.get_data(as_text=True) == "Hola, Ben!"


def test_hello_responde_200():
    cliente = app.test_client()
    respuesta = cliente.get('/hello?name=Jenkins')
    assert respuesta.status_code == 200