// src/lib/nhl/colors.ts
export const nhlTeamColors: Record<string, { primary: string; secondary: string }> = {
  ANA: { primary: "#F47A38", secondary: "#B9975B" }, // Ducks
  ARI: { primary: "#8C2633", secondary: "#E2D6B5" }, // Coyotes
  BOS: { primary: "#FFB81C", secondary: "#000000" }, // Bruins
  BUF: { primary: "#003087", secondary: "#FFB81C" }, // Sabres
  CGY: { primary: "#C8102E", secondary: "#F1BE48" }, // Flames
  CAR: { primary: "#CC0000", secondary: "#000000" }, // Hurricanes
  CHI: { primary: "#CF0A2C", secondary: "#000000" }, // Blackhawks
  COL: { primary: "#6F263D", secondary: "#236192" }, // Avalanche
  CBJ: { primary: "#002654", secondary: "#CE1126" }, // Blue Jackets
  DAL: { primary: "#006847", secondary: "#8F8F8C" }, // Stars
  DET: { primary: "#CE1126", secondary: "#FFFFFF" }, // Red Wings
  EDM: { primary: "#041E42", secondary: "#FF4C00" }, // Oilers
  FLA: { primary: "#041E42", secondary: "#C8102E" }, // Panthers
  LAK: { primary: "#111111", secondary: "#A2AAAD" }, // Kings
  MIN: { primary: "#154734", secondary: "#A6192E" }, // Wild
  MTL: { primary: "#AF1E2D", secondary: "#192168" }, // Canadiens
  NSH: { primary: "#FFB81C", secondary: "#041E42" }, // Predators
  NJD: { primary: "#CE1126", secondary: "#000000" }, // Devils
  NYI: { primary: "#00539B", secondary: "#F47D30" }, // Islanders
  NYR: { primary: "#0038A8", secondary: "#CE1126" }, // Rangers
  OTT: { primary: "#C8102E", secondary: "#C69214" }, // Senators
  PHI: { primary: "#F74902", secondary: "#000000" }, // Flyers
  PIT: { primary: "#FFB81C", secondary: "#000000" }, // Penguins
  SJS: { primary: "#006D75", secondary: "#EA7200" }, // Sharks
  SEA: { primary: "#99D9D9", secondary: "#001628" }, // Kraken
  STL: { primary: "#002F87", secondary: "#FCB514" }, // Blues
  TBL: { primary: "#002868", secondary: "#FFFFFF" }, // Lightning
  TOR: { primary: "#00205B", secondary: "#FFFFFF" }, // Maple Leafs
  VAN: { primary: "#00205B", secondary: "#00843D" }, // Canucks
  VGK: { primary: "#B4975A", secondary: "#333F48" }, // Golden Knights
  WSH: { primary: "#041E42", secondary: "#C8102E" }, // Capitals
  WPG: { primary: "#041E42", secondary: "#AC162C" }, // Jets
};

// convenient getter
export const getTeamColor = (abbr: string) =>
  nhlTeamColors[abbr] ?? { primary: "#999999", secondary: "#333333" };
