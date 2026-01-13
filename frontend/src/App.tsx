import { Shield } from 'lucide-react';

export const App = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-quantum-900 to-quantum-700">
      <div className="container mx-auto px-4 py-12">
        <div className="text-center text-white mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="w-10 h-10" />
            <h1 className="text-4xl font-bold">QuantumShield Vault</h1>
          </div>
          <p className="text-lg text-quantum-100">
            Protecting crypto wallets from quantum computing attacks expected by 2027
          </p>
        </div>

        <div className="max-w-6xl mx-auto bg-white rounded-lg shadow-xl overflow-hidden">
          <div className="p-8">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold mb-3">Welcome to QuantumShield Vault</h2>
              <p className="text-gray-600">
                The first wallet protection system for the post-quantum era.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="text-3xl mb-2">🔐</div>
                <h3 className="font-bold mb-2">ECDSA Wallets</h3>
                <p className="text-sm text-gray-600">
                  Traditional secp256k1 wallets currently used in blockchain.
                </p>
              </div>
              <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="text-3xl mb-2">⚡</div>
                <h3 className="font-bold mb-2">Quantum Attack Simulator</h3>
                <p className="text-sm text-gray-600">
                  Test how vulnerable your ECDSA keys are to Shor's algorithm.
                </p>
              </div>
              <div className="border rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="text-3xl mb-2">🛡️</div>
                <h3 className="font-bold mb-2">Dilithium Migration</h3>
                <p className="text-sm text-gray-600">
                  Migrate to post-quantum cryptography resistant to quantum attacks.
                </p>
              </div>
            </div>

            <div className="bg-quantum-50 border border-quantum-200 rounded-lg p-6 mb-8">
              <h3 className="font-bold mb-3">🚨 The Quantum Threat (2027)</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• ECDSA secp256k1 can be broken by sufficiently large quantum computers</li>
                <li>• Shor's algorithm runs in polynomial time on quantum computers (vs exponential on classical)</li>
                <li>• Estimated break time: ~30 seconds with 10+ million qubits</li>
                <li>• Dilithium is part of NIST's PQC (Post-Quantum Cryptography) standards</li>
              </ul>
            </div>

            <div className="text-center text-gray-600 text-sm">
              <p>
                API Documentation: <code className="bg-gray-100 px-2 py-1 rounded">localhost:8000/docs</code>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
