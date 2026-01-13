import { useState } from 'react';
import { Brain, ArrowRight, Loader } from 'lucide-react';
import { migrateWallet } from '../lib/api';

interface MigrationAgentProps {
  walletId: number;
  isMigrated: boolean;
  onMigrationComplete?: () => void;
}

export const MigrationAgent: React.FC<MigrationAgentProps> = ({
  walletId,
  isMigrated,
  onMigrationComplete,
}) => {
  const [migrating, setMigrating] = useState(false);
  const [migrationPhase, setMigrationPhase] = useState<string | null>(null);
  const [migrationComplete, setMigrationComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMigrate = async () => {
    try {
      setMigrating(true);
      setError(null);
      setMigrationPhase('Generating Dilithium keys...');

      await new Promise((resolve) => setTimeout(resolve, 800));
      setMigrationPhase('Transferring balance...');

      await new Promise((resolve) => setTimeout(resolve, 600));
      setMigrationPhase('Verifying signatures...');

      await new Promise((resolve) => setTimeout(resolve, 600));
      setMigrationPhase('Finalizing migration...');

      await migrateWallet(walletId);

      setMigrationComplete(true);
      setMigrationPhase(null);
      onMigrationComplete?.();
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Migration failed'
      );
      setMigrationPhase(null);
    } finally {
      setMigrating(false);
    }
  };

  if (isMigrated) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="w-6 h-6 text-green-600" />
          <h2 className="text-xl font-bold text-green-700">Migration Agent</h2>
        </div>
        <div className="flex items-center gap-2 text-green-700">
          <div className="w-4 h-4 rounded-full bg-green-600"></div>
          <p className="font-semibold">Wallet already migrated to Dilithium ✓</p>
        </div>
        <p className="text-sm text-green-600 mt-2">
          Your wallet is protected against quantum attacks.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <Brain className="w-6 h-6 text-quantum-600" />
        <h2 className="text-xl font-bold">AI Migration Agent</h2>
      </div>

      <p className="text-gray-600 mb-4">
        Automated key rotation from ECDSA to post-quantum Dilithium cryptography.
        The AI agent plans and executes migration with zero downtime.
      </p>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {migrationPhase && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Loader className="w-4 h-4 text-blue-600 animate-spin" />
            <p className="font-semibold text-blue-700">{migrationPhase}</p>
          </div>
          <div className="flex gap-1">
            {['Keygen', 'Transfer', 'Verify', 'Finalize'].map((phase, idx) => (
              <div
                key={idx}
                className="flex-1 h-1 bg-blue-200 rounded-full overflow-hidden"
              >
                <div
                  className="h-full bg-blue-600 transition-all duration-500"
                  style={{
                    width:
                      migrationPhase.includes(phase) ||
                      (migrationPhase.includes('Finalizing') &&
                        idx < 3)
                        ? '100%'
                        : '0%',
                  }}
                ></div>
              </div>
            ))}
          </div>
        </div>
      )}

      {migrationComplete && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-700 font-semibold mb-2">
            ✓ Migration Successful!
          </p>
          <p className="text-sm text-green-600">
            Your wallet keys have been migrated to Dilithium post-quantum cryptography.
            Your funds are now protected against quantum attacks expected by 2027.
          </p>
        </div>
      )}

      <div className="space-y-3">
        <div className="bg-gradient-to-r from-quantum-50 to-quantum-100 p-3 rounded-lg">
          <p className="text-sm font-semibold text-quantum-900 mb-2">
            Migration Plan (AI-Generated):
          </p>
          <ol className="text-sm text-quantum-800 space-y-1">
            <li className="flex items-center gap-2">
              <span className="font-bold">1.</span> Generate Dilithium keypair (5s)
            </li>
            <li className="flex items-center gap-2">
              <span className="font-bold">2.</span> Transfer balance (1.0 QSV)
            </li>
            <li className="flex items-center gap-2">
              <span className="font-bold">3.</span> Verify post-quantum signatures
            </li>
            <li className="flex items-center gap-2">
              <span className="font-bold">4.</span> Update wallet (complete)
            </li>
          </ol>
        </div>

        <button
          onClick={handleMigrate}
          disabled={migrating}
          className="w-full bg-quantum-600 hover:bg-quantum-700 disabled:bg-gray-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors flex items-center justify-center gap-2"
        >
          {migrating ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Migrating...
            </>
          ) : (
            <>
              <ArrowRight className="w-4 h-4" />
              Start Quantum-Safe Migration
            </>
          )}
        </button>

        <div className="text-xs text-gray-500 flex items-start gap-2">
          <span className="text-lg mt-0.5">ℹ️</span>
          <div>
            This will create new Dilithium keys resistant to quantum attacks.
            Your ECDSA keys remain for backwards compatibility.
          </div>
        </div>
      </div>
    </div>
  );
};
