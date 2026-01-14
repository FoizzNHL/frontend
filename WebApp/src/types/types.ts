export type NhlGoalScorer = {
  fullName?: string;
  number?: number | string;
  team?: string;
  headshot?: string;
};

export type NhlGoal = {
  scorer?: NhlGoalScorer;
  period?: number;
  timeInPeriod?: string;
  strength?: string;
  awayScore?: number;
  homeScore?: number;
  highlight?: {
    url?: string;
  };
};

type NhlScoreTeam = {
  abbr: string;
  score: number;
};

export type NhlScore = {
  id?: string;
  date?: string;
  state?: string;
  home: NhlScoreTeam;
  away: NhlScoreTeam;
  noGame?: boolean;
  message?: string;
};


export type NhlGoalsResponse = {
  home?: { abbr: string };
  away?: { abbr: string };
  goals: NhlGoal[];
};

type Rgb =
  | { r: number; g: number; b: number }
  | [number, number, number]; // covers both object or tuple styles if hexToRgb ever changes

type FaceType = "happy" | "sad" | "stressed";

type FaceCommand = {
  face: FaceType;
  color: Rgb;
  bg: Rgb;
};

type GoalAnimationCommand = {
  animation: "habs_goal"; // extend later if you add more animations
  player_number?: number | string;
  duration?: number;
};

export type LedCommand = FaceCommand | GoalAnimationCommand;