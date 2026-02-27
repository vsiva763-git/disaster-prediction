from src.web_app import create_app

app = create_app()
with app.test_client() as c:
    resp = c.get('/health')
    print('Status:', resp.status_code)
    print('Body:', resp.get_data(as_text=True))
