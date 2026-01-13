import { useState } from 'react';
import { Zap, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { simulateAttack } from '../lib/api';
import { AttackResult } from '../lib/types';

interface AttackSimulatorProps {
  walletId: number;
  isMigrated: boolean;
  onAttackComplete?: (result: AttackResult) => void;
}

export const AttackSimulator: React.FC<AttackSimulatorProps> = ({
  walletId,
  isMigrated,
  onAttackComplete,
}) => {
  const [attacking, setAttacking] = useState(false);
  const [result, setResult] = useState<AttackResult | null>(null);
  const [simulating, setSimulating] = useState(false);

  const handleSimulateAttack = async () => {
    try {
      setAttacking(true);
      setSimulating(true);

      // Simulate attack animation
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const response = await simulateAttack(walletId);
      setResult(response.data);
      onAttackComplete?.(response.data);
    } catch (error) {
      console.error('Attack simulation failed:', error);
    } finally {
      setAttacking(false);
      setSimulating(false);
    }
  };

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <Zap className="w-6 h-6 text-yellow-600" />
        <h2 className="text-xl font-bold">Quantum Attack Simulator</h2>
      </div>

      <p className="text-gray-600 mb-4">
        Test if your wallet can withstand Shor's algorithm quantum attack expected by 2027.
      </p>

      <button
        onClick={handleSimulateAttack}
        disabled={attacking}
        className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
      >
        <Zap className="w-4 h-4" />
        {attacking ? 'Simulating Attack...' : 'Simulate Quantum Attack'}
      </button>

      {simulating && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-4 h-4 text-yellow-600 animate-spin" />
            <p className="text-sm font-semibold text-yellow-700">
              Running Shor's algorithm simulation...
            </p>
          </div>
          <p className="text-xs text-yellow-600">
            Attempting to break ECDSA secp256k1 signature...
          </p>
        </div>
      )}

      {result && (
        <div
          className={`mt-4 p-4 border rounded-lg ${
            result.attack_successful
              ? 'bg-red-50 border-red-200'
              : 'bg-green-50 border-green-200'
          }`}
        >
          <div className="flex items-start gap-3">
            {result.attack_successful ? (
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            ) : (
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <h3
                className={`font-semibold mb-2 ${
                  result.attack_successful ? 'text-red-700' : 'text-green-700'
                }`}
              >
                {result.attack_successful
                  ? '🚨 Attack Successful!'
                  : '✓ Attack Failed'}
              </h3>
              <p
                className={`text-sm mb-3 ${
                  result.attack_successful
                    ? 'text-red-600'
                    : 'text-green-600'
                }`}
              >
                {result.message}
              </p>

              <div className="bg-white bg-opacity-50 rounded p-2 mb-3 text-xs">
                <p className="text-gray-700">
                  <strong>Algorithm:</strong>{' '}
                  {result.attack_successful ? 'ECDSA-secp256k1' : 'Dilithium'}
                </p>
                <p className="text-gray-700">
                  <strong>Break Time:</strong>{' '}
                  {result.estimated_break_time_seconds === Infinity
                    ? 'No known algorithm'
                    : `~${result.estimated_break_time_seconds}s`}
                </p>
                <p className="text-gray-700">
                  <strong>Signature Integrity:</strong>{' '}
                  {result.signature_broken ? '❌ Broken' : '✓ Intact'}
                </p>
              </div>

              <p
                className={`text-sm font-semibold ${
                  result.attack_successful
                    ? 'text-red-700'
                    : 'text-green-700'
                }`}
              >
                💡 {result.recommendation}
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
        <p>
          <strong>How it works:</strong> This simulator demonstrates Shor's algorithm,
          which can factor large numbers exponentially faster on quantum computers,
          breaking ECDSA signatures. Dilithium is resistant to both classical and
          quantum attacks.
        </p>
      </div>
    </div>
  );
};
