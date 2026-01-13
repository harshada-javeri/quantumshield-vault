import { useState, useEffect } from 'react';
import { Shield, Key, AlertTriangle, CheckCircle } from 'lucide-react';
import { getDashboard, getMigrationStats } from '../lib/api';
import { formatAddress, formatBalance, formatDate } from '../lib/utils';
import { Wallet, MigrationLog } from '../lib/types';

interface DashboardProps {
  userId: number;
}

export const WalletDashboard: React.FC<DashboardProps> = ({ userId }) => {
  const [wallets, setWallets] = useState<Wallet[]>([]);
  const [migrations, setMigrations] = useState<MigrationLog[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        const [dashboardRes, statsRes] = await Promise.all([
          getDashboard(userId),
          getMigrationStats(),
        ]);

        setWallets(dashboardRes.data.wallets);
        setMigrations(dashboardRes.data.migration_logs);
        setStats(statsRes.data);
        setError(null);
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [userId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <Shield className="w-8 h-8 animate-spin mx-auto mb-2" />
          <p className="text-gray-600">Loading wallet data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-quantum-600 to-quantum-900 text-white p-6 rounded-lg">
        <div className="flex items-center gap-3">
          <Shield className="w-8 h-8" />
          <h1 className="text-3xl font-bold">QuantumShield Vault</h1>
        </div>
        <p className="text-quantum-100 mt-2">
          Post-quantum cryptographic wallet protection against 2027 quantum threat
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border rounded-lg p-4">
          <p className="text-gray-600 text-sm">Total Wallets</p>
          <p className="text-2xl font-bold">{wallets.length}</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <p className="text-gray-600 text-sm flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-600" />
            Migrated (Secure)
          </p>
          <p className="text-2xl font-bold text-green-600">
            {wallets.filter((w) => w.is_migrated).length}
          </p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-gray-600 text-sm flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            Vulnerable
          </p>
          <p className="text-2xl font-bold text-red-600">
            {wallets.filter((w) => !w.is_migrated).length}
          </p>
        </div>
      </div>

      {/* Global Stats */}
      {stats && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-gray-600">Network-wide Migration Progress</p>
          <div className="mt-2">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold">
                {stats.migrated_wallets} / {stats.total_wallets} wallets migrated
              </span>
              <span className="text-lg font-bold text-blue-600">
                {stats.migration_percentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${stats.migration_percentage}%` }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {/* Wallets Section */}
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Your Wallets</h2>
        {wallets.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No wallets yet. Create one to get started!</p>
        ) : (
          <div className="space-y-3">
            {wallets.map((wallet) => (
              <WalletCard key={wallet.id} wallet={wallet} />
            ))}
          </div>
        )}
      </div>

      {/* Migrations History */}
      {migrations.length > 0 && (
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Migration History</h2>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {migrations.map((migration) => (
              <div
                key={migration.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg text-sm"
              >
                <div>
                  <p className="font-semibold">{`Wallet ${migration.wallet_id}`}</p>
                  <p className="text-gray-600">
                    {formatDate(migration.created_at)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{formatBalance(migration.transferred_balance)} QSV</p>
                  <p className={`text-xs font-semibold ${
                    migration.status === 'completed' ? 'text-green-600' : 'text-yellow-600'
                  }`}>
                    {migration.status.toUpperCase()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

interface WalletCardProps {
  wallet: Wallet;
}

const WalletCard: React.FC<WalletCardProps> = ({ wallet }) => {
  return (
    <div
      className={`p-4 border rounded-lg ${
        wallet.is_migrated
          ? 'bg-green-50 border-green-200'
          : 'bg-red-50 border-red-200'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            {wallet.is_migrated ? (
              <>
                <Key className="w-4 h-4 text-green-600" />
                <span className="font-semibold text-green-700">{wallet.name}</span>
                <span className="text-xs bg-green-200 text-green-700 px-2 py-1 rounded">
                  Dilithium Protected
                </span>
              </>
            ) : (
              <>
                <AlertTriangle className="w-4 h-4 text-red-600" />
                <span className="font-semibold text-red-700">{wallet.name}</span>
                <span className="text-xs bg-red-200 text-red-700 px-2 py-1 rounded">
                  Vulnerable
                </span>
              </>
            )}
          </div>
          <p className="text-sm text-gray-600">
            Address: <code className="bg-gray-100 px-2 py-1 rounded text-xs">
              {formatAddress(wallet.ecdsa_address)}
            </code>
          </p>
          <p className="text-sm text-gray-600 mt-1">
            Balance: <span className="font-semibold">{formatBalance(wallet.balance_qsv)} QSV</span>
          </p>
          {wallet.migrated_at && (
            <p className="text-xs text-gray-500 mt-1">
              Migrated: {formatDate(wallet.migrated_at)}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};
