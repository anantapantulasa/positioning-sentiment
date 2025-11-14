// Optimal thresholds loaded from CSV
// Format: X, Y, Z (Long: Commercials, Large, Small), A, B, C (Short: Commercials, Large, Small)
const OPTIMAL_THRESHOLDS = {
  gold: {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 90 }
  },
  coffee: {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 90 }
  },
  // Add more commodities as needed
  ym: {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 95 }
  },
  '2yr_ZT': {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 90 }
  },
  '10yr_ZB': {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 90 }
  },
  cattle: {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 95 }
  },
  nq: {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 95 }
  },
  silver: {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 5 },
    short: { commercials: 10, largeSpeculators: 90, smallSpeculators: 90 }
  },
  copper: {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 90 }
  },
  es: {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 95 }
  },
  '30yr_UB': {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 90 }
  },
  rty: {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 90 }
  },
  yen: {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 95 }
  },
  '5yr_ZF': {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 95 }
  },
  soybean_oil: {
    long: { commercials: 95, largeSpeculators: 10, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 95 }
  },
  nkd: {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 90 }
  },
  cotton: {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 90 }
  },
  dollar: {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 95 }
  },
  sugar: {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 95 }
  },
  euro: {
    long: { commercials: 85, largeSpeculators: 5, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 90 }
  },
  corn: {
    long: { commercials: 95, largeSpeculators: 10, smallSpeculators: 10 },
    short: { commercials: 5, largeSpeculators: 90, smallSpeculators: 95 }
  },
  cocoa: {
    long: { commercials: 85, largeSpeculators: 10, smallSpeculators: 5 },
    short: { commercials: 5, largeSpeculators: 95, smallSpeculators: 95 }
  }
}

export function getOptimalThresholds(commodityKey) {
  return OPTIMAL_THRESHOLDS[commodityKey] || null
}

