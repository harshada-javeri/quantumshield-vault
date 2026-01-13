import { describe, it, expect } from 'vitest';
import { formatAddress, formatBalance, getAlgorithmStatus } from '../src/lib/utils';

describe('Utility Functions', () => {
  describe('formatAddress', () => {
    it('should shorten long addresses', () => {
      const address = '0x1234567890abcdefghijklmnopqrstuvwxyz';
      const result = formatAddress(address);
      expect(result).toBe('0x1234...wxyz');
    });

    it('should return short addresses unchanged', () => {
      const address = '0x123456';
      expect(formatAddress(address)).toBe(address);
    });

    it('should handle empty strings', () => {
      expect(formatAddress('')).toBe('');
    });
  });

  describe('formatBalance', () => {
    it('should format balance to 4 decimals', () => {
      expect(formatBalance(1.23456789)).toBe('1.2346');
    });

    it('should handle zero balance', () => {
      expect(formatBalance(0)).toBe('0.0000');
    });

    it('should handle large numbers', () => {
      expect(formatBalance(999999.9999)).toBe('999999.9999');
    });
  });

  describe('getAlgorithmStatus', () => {
    it('should return quantum-safe status for migrated wallet', () => {
      expect(getAlgorithmStatus(true)).toBe('Quantum-Safe ✓');
    });

    it('should return vulnerable status for non-migrated wallet', () => {
      expect(getAlgorithmStatus(false)).toBe('Vulnerable ⚠️');
    });
  });
});
