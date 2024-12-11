from OpenSSL import crypto
import os

def generate_self_signed_cert():
    # Generate key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Generate certificate
    cert = crypto.X509()
    cert.get_subject().C = "NL"  # Country
    cert.get_subject().ST = "Noord-Holland"  # State
    cert.get_subject().L = "Amsterdam"  # Locality
    cert.get_subject().O = "Event Management App"  # Organization
    cert.get_subject().OU = "Development"  # Organizational Unit
    cert.get_subject().CN = "localhost"  # Common Name
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    # Create cert directory if it doesn't exist
    os.makedirs('cert', exist_ok=True)

    # Save private key
    with open("cert/key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    # Save certificate
    with open("cert/cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    print("Certificate and private key have been generated in the 'cert' directory.")

if __name__ == '__main__':
    generate_self_signed_cert()