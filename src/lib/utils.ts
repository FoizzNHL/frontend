export function formatDate(date: Date, format: string) {
  const yyyy = date.getFullYear().toString();
  const mm = (date.getMonth() + 1).toString().padStart(2, "0");
  const dd = date.getDate().toString().padStart(2, "0");

  return format.replace("yy", yyyy).replace("mm", mm).replace("dd", dd);
}

// Convert hex color to RGB array
export const hexToRgb = (hex: string) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? [
        parseInt(result[1], 16),
        parseInt(result[2], 16),
        parseInt(result[3], 16),
      ]
    : [255, 0, 0];
};

export function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}