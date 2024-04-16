export type LetterChallenge = [letter: string, image: string];
export type WordChallenge = [letter: string, image: string[]];

const LETTER_PATH = "/letterImages/";

export const ALPHABET = "abcdefghijklmnopqrstuvwxyz".toUpperCase().split("");
export const alphabetChallenges: LetterChallenge[] = ALPHABET.reduce(
  (prev: LetterChallenge[], cur: string) => {
    prev.push([cur, LETTER_PATH + cur.toLowerCase() + ".png"]);
    return prev;
  },
  []
);

const words =
  // "why?4eNt91uV02o:35300,information?oY4zNmRl79Q:639180,ch?rBNUou5ZsBM:11711#rBNUou5ZsBM:151317,if?rBNUou5ZsBM:16716#rBNUou5ZsBM:33166#rBNUou5ZsBM:36970#rBNUou5ZsBM:41141#rBNUou5ZsBM:175008,he?rBNUou5ZsBM:18651#rBNUou5ZsBM:54320,gr?rBNUou5ZsBM:24858,be?rBNUou5ZsBM:27393#rBNUou5ZsBM:97697#rBNUou5ZsBM:167934#rBNUou5ZsBM:179846,ha?rBNUou5ZsBM:38638#rBNUou5ZsBM:73540,as?rBNUou5ZsBM:51918,we?rBNUou5ZsBM:56589,yo?rBNUou5ZsBM:59759,mo?rBNUou5ZsBM:62529,it?rBNUou5ZsBM:64898,ho?rBNUou5ZsBM:65598,so?rBNUou5ZsBM:79078,an?rBNUou5ZsBM:83283#rBNUou5ZsBM:184117,st?rBNUou5ZsBM:89689,ah?rBNUou5ZsBM:93026,by?rBNUou5ZsBM:103236,fa?rBNUou5ZsBM:108942,en?rBNUou5ZsBM:119752,bu?rBNUou5ZsBM:122322#rBNUou5ZsBM:145945,in?rBNUou5ZsBM:136669,is?rBNUou5ZsBM:155521#rBNUou5ZsBM:158091#rBNUou5ZsBM:165331,sh?rBNUou5ZsBM:172338,wow?aq_Ic15YnQY:377780#aq_Ic15YnQY:531140,good?aq_Ic15YnQY:468440,yes?bKTcufCpgpA:32355";
  "ch?rBNUou5ZsBM:11711#rBNUou5ZsBM:151317,if?rBNUou5ZsBM:16716#rBNUou5ZsBM:33166#rBNUou5ZsBM:36970#rBNUou5ZsBM:41141#rBNUou5ZsBM:175008,he?rBNUou5ZsBM:18651#rBNUou5ZsBM:54320,gr?rBNUou5ZsBM:24858,be?rBNUou5ZsBM:27393#rBNUou5ZsBM:97697#rBNUou5ZsBM:167934#rBNUou5ZsBM:179846,ha?rBNUou5ZsBM:38638#rBNUou5ZsBM:73540,as?rBNUou5ZsBM:51918,we?rBNUou5ZsBM:56589,yo?rBNUou5ZsBM:59759,mo?rBNUou5ZsBM:62529,it?rBNUou5ZsBM:64898,ho?rBNUou5ZsBM:65598,so?rBNUou5ZsBM:79078,an?rBNUou5ZsBM:83283#rBNUou5ZsBM:184117,st?rBNUou5ZsBM:89689,ah?rBNUou5ZsBM:93026,by?rBNUou5ZsBM:103236,fa?rBNUou5ZsBM:108942,en?rBNUou5ZsBM:119752,bu?rBNUou5ZsBM:122322#rBNUou5ZsBM:145945,in?rBNUou5ZsBM:136669,is?rBNUou5ZsBM:155521#rBNUou5ZsBM:158091#rBNUou5ZsBM:165331,sh?rBNUou5ZsBM:172338,wow?aq_Ic15YnQY:377780#aq_Ic15YnQY:531140,good?aq_Ic15YnQY:468440,yes?bKTcufCpgpA:32355";
export const commonSignsChallenges: WordChallenge[] = words
  .split(",")
  .map((sign: string): WordChallenge => {
    let word = sign.split("?")[0];
    let clips = sign.split("?")[1].split("#");
    return [word, clips];
  });
