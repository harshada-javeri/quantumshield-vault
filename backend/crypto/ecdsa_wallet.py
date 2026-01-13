"""ECDSA secp256k1 wallet implementation (currently vulnerable to quantum attacks)."""

import hashlib
from typing import Tuple
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend


class ECDSAWallet:
    """ECDSA secp256k1 wallet for traditional blockchain operations."""

    CURVE = ec.SECP256K1()
    BACKEND = default_backend()

    @staticmethod
    def generate_keypair() -> Tuple[str, str, str]:
        """
        Generate ECDSA secp256k1 keypair and derive address.

        Returns:
            Tuple of (private_key_hex, public_key_hex, address)
        """
        # Generate private key
        private_key = ec.generate_private_key(ECDSAWallet.CURVE, ECDSAWallet.BACKEND)

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        # Derive address (simplified: hash of public key)
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint,
        )
        address = "0x" + hashlib.sha256(public_bytes).hexdigest()[:40]

        return private_pem, public_pem, address

    @staticmethod
    def sign_message(private_key_pem: str, message: str) -> str:
        """
        Sign a message with ECDSA private key.

        Args:
            private_key_pem: PEM-encoded private key
            message: Message to sign

        Returns:
            Signature in hex format
        """
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode("utf-8"), password=None, backend=ECDSAWallet.BACKEND
        )

        signature = private_key.sign(
            message.encode("utf-8"),
            ec.ECDSA(hashes.SHA256()),
        )

        return signature.hex()

    @staticmethod
    def verify_signature(public_key_pem: str, message: str, signature_hex: str) -> bool:
        """
        Verify ECDSA signature.

        Args:
            public_key_pem: PEM-encoded public key
            message: Original message
            signature_hex: Signature in hex format

        Returns:
            True if signature is valid
        """
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode("utf-8"), backend=ECDSAWallet.BACKEND
            )

            public_key.verify(
                bytes.fromhex(signature_hex),
                message.encode("utf-8"),
                ec.ECDSA(hashes.SHA256()),
            )
            return True
        except Exception:
            return False

    @staticmethod
    def get_key_fingerprint(public_key_pem: str) -> str:
        """Get SHA256 fingerprint of public key."""
        return hashlib.sha256(public_key_pem.encode()).hexdigest()[:16]
