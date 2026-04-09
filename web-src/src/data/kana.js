// web-src/src/data/kana.js
// Kana character data for the quiz. Groups are derived from Unicode NFD decomposition:
// multi-char → combination; base+combining-mark → dakuten; else → basic.
function _group(char) {
  if (char.length > 1) return 'combination'
  if (char.normalize('NFD').length > 1) return 'dakuten'
  return 'basic'
}

const _H = [
  // Basic (46)
  ['あ','a','a'],['い','i','a'],['う','u','a'],['え','e','a'],['お','o','a'],
  ['か','ka','ka'],['き','ki','ka'],['く','ku','ka'],['け','ke','ka'],['こ','ko','ka'],
  ['さ','sa','sa'],['し','shi','sa'],['す','su','sa'],['せ','se','sa'],['そ','so','sa'],
  ['た','ta','ta'],['ち','chi','ta'],['つ','tsu','ta'],['て','te','ta'],['と','to','ta'],
  ['な','na','na'],['に','ni','na'],['ぬ','nu','na'],['ね','ne','na'],['の','no','na'],
  ['は','ha','ha'],['ひ','hi','ha'],['ふ','fu','ha'],['へ','he','ha'],['ほ','ho','ha'],
  ['ま','ma','ma'],['み','mi','ma'],['む','mu','ma'],['め','me','ma'],['も','mo','ma'],
  ['や','ya','ya'],['ゆ','yu','ya'],['よ','yo','ya'],
  ['ら','ra','ra'],['り','ri','ra'],['る','ru','ra'],['れ','re','ra'],['ろ','ro','ra'],
  ['わ','wa','wa'],['を','wo','wa'],['ん','n','n'],
  // Dakuten (25)
  ['が','ga','ka'],['ぎ','gi','ka'],['ぐ','gu','ka'],['げ','ge','ka'],['ご','go','ka'],
  ['ざ','za','sa'],['じ','ji','sa'],['ず','zu','sa'],['ぜ','ze','sa'],['ぞ','zo','sa'],
  ['だ','da','ta'],['ぢ','ji','ta'],['づ','zu','ta'],['で','de','ta'],['ど','do','ta'],
  ['ば','ba','ha'],['び','bi','ha'],['ぶ','bu','ha'],['べ','be','ha'],['ぼ','bo','ha'],
  ['ぱ','pa','ha'],['ぴ','pi','ha'],['ぷ','pu','ha'],['ぺ','pe','ha'],['ぽ','po','ha'],
  // Combinations (36)
  ['きゃ','kya','ka'],['きゅ','kyu','ka'],['きょ','kyo','ka'],
  ['しゃ','sha','sa'],['しゅ','shu','sa'],['しょ','sho','sa'],
  ['ちゃ','cha','ta'],['ちゅ','chu','ta'],['ちょ','cho','ta'],
  ['にゃ','nya','na'],['にゅ','nyu','na'],['にょ','nyo','na'],
  ['ひゃ','hya','ha'],['ひゅ','hyu','ha'],['ひょ','hyo','ha'],
  ['みゃ','mya','ma'],['みゅ','myu','ma'],['みょ','myo','ma'],
  ['りゃ','rya','ra'],['りゅ','ryu','ra'],['りょ','ryo','ra'],
  ['ぎゃ','gya','ka'],['ぎゅ','gyu','ka'],['ぎょ','gyo','ka'],
  ['じゃ','ja','sa'],['じゅ','ju','sa'],['じょ','jo','sa'],
  ['ぢゃ','ja','ta'],['ぢゅ','ju','ta'],['ぢょ','jo','ta'],
  ['びゃ','bya','ha'],['びゅ','byu','ha'],['びょ','byo','ha'],
  ['ぴゃ','pya','ha'],['ぴゅ','pyu','ha'],['ぴょ','pyo','ha'],
].map(([char, romaji, row]) => ({ char, romaji, row, group: _group(char), script: 'hiragana' }))

const _K = [
  // Basic (46)
  ['ア','a','a'],['イ','i','a'],['ウ','u','a'],['エ','e','a'],['オ','o','a'],
  ['カ','ka','ka'],['キ','ki','ka'],['ク','ku','ka'],['ケ','ke','ka'],['コ','ko','ka'],
  ['サ','sa','sa'],['シ','shi','sa'],['ス','su','sa'],['セ','se','sa'],['ソ','so','sa'],
  ['タ','ta','ta'],['チ','chi','ta'],['ツ','tsu','ta'],['テ','te','ta'],['ト','to','ta'],
  ['ナ','na','na'],['ニ','ni','na'],['ヌ','nu','na'],['ネ','ne','na'],['ノ','no','na'],
  ['ハ','ha','ha'],['ヒ','hi','ha'],['フ','fu','ha'],['ヘ','he','ha'],['ホ','ho','ha'],
  ['マ','ma','ma'],['ミ','mi','ma'],['ム','mu','ma'],['メ','me','ma'],['モ','mo','ma'],
  ['ヤ','ya','ya'],['ユ','yu','ya'],['ヨ','yo','ya'],
  ['ラ','ra','ra'],['リ','ri','ra'],['ル','ru','ra'],['レ','re','ra'],['ロ','ro','ra'],
  ['ワ','wa','wa'],['ヲ','wo','wa'],['ン','n','n'],
  // Dakuten (25)
  ['ガ','ga','ka'],['ギ','gi','ka'],['グ','gu','ka'],['ゲ','ge','ka'],['ゴ','go','ka'],
  ['ザ','za','sa'],['ジ','ji','sa'],['ズ','zu','sa'],['ゼ','ze','sa'],['ゾ','zo','sa'],
  ['ダ','da','ta'],['ヂ','ji','ta'],['ヅ','zu','ta'],['デ','de','ta'],['ド','do','ta'],
  ['バ','ba','ha'],['ビ','bi','ha'],['ブ','bu','ha'],['ベ','be','ha'],['ボ','bo','ha'],
  ['パ','pa','ha'],['ピ','pi','ha'],['プ','pu','ha'],['ペ','pe','ha'],['ポ','po','ha'],
  // Combinations (36)
  ['キャ','kya','ka'],['キュ','kyu','ka'],['キョ','kyo','ka'],
  ['シャ','sha','sa'],['シュ','shu','sa'],['ショ','sho','sa'],
  ['チャ','cha','ta'],['チュ','chu','ta'],['チョ','cho','ta'],
  ['ニャ','nya','na'],['ニュ','nyu','na'],['ニョ','nyo','na'],
  ['ヒャ','hya','ha'],['ヒュ','hyu','ha'],['ヒョ','hyo','ha'],
  ['ミャ','mya','ma'],['ミュ','myu','ma'],['ミョ','myo','ma'],
  ['リャ','rya','ra'],['リュ','ryu','ra'],['リョ','ryo','ra'],
  ['ギャ','gya','ka'],['ギュ','gyu','ka'],['ギョ','gyo','ka'],
  ['ジャ','ja','sa'],['ジュ','ju','sa'],['ジョ','jo','sa'],
  ['ヂャ','ja','ta'],['ヂュ','ju','ta'],['ヂョ','jo','ta'],
  ['ビャ','bya','ha'],['ビュ','byu','ha'],['ビョ','byo','ha'],
  ['ピャ','pya','ha'],['ピュ','pyu','ha'],['ピョ','pyo','ha'],
].map(([char, romaji, row]) => ({ char, romaji, row, group: _group(char), script: 'katakana' }))

export const HIRAGANA = _H
export const KATAKANA = _K
export const ALL_KANA = [..._H, ..._K]
