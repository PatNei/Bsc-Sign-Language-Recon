type Challenge = [letter: string, image: string];

const PATH = "/public/letterImages/";

export const ALPHABET = "abcdefghijklmnopqrstuvwxyz".toUpperCase().split("");
export const CHALLENGES: Challenge[] = ALPHABET.reduce(
  (prev: Challenge[], cur: string) => {
    prev.push([cur, PATH + cur.toLowerCase() + ".png"]);
    return prev;
  },
  []
);
