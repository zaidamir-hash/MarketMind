export function formatDateTime(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function formatNumber(value, options = {}) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }

  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 4,
    ...options,
  }).format(number);
}

export function formatCurrency(value, currency = "USD") {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(number);
}

export function formatPercent(value) {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  const number = Number(value);
  if (Number.isNaN(number)) {
    return String(value);
  }

  return `${(number * 100).toFixed(2)}%`;
}

export function clampText(value, fallback = "-") {
  return value ?? fallback;
}
