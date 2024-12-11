from app import create_app
import os

app = create_app()

def get_ssl_context():
    cert_dir = 'cert'
    cert_file = os.path.join(cert_dir, 'cert.pem')
    key_file = os.path.join(cert_dir, 'key.pem')
    
    # Check if certificate exists, if not generate it
    if not (os.path.exists(cert_file) and os.path.exists(key_file)):
        print("No SSL certificate found. Generating self-signed certificate...")
        from generate_cert import generate_self_signed_cert
        generate_self_signed_cert()
    
    return (cert_file, key_file)

if __name__ == '__main__':
    ssl_context = get_ssl_context()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        ssl_context=ssl_context
    )