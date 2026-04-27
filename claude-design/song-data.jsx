// Shared song data — same lyrics/chords rendered with different section tag styles.
// Mirrors the reference screenshot: Terra Seca by Fraternidade São João Paulo II.

const SONG = [
  { type: 'intro', label: 'Intro', lines: [
    { chords: 'F   G   Em  Am', lyric: '' },
    { chords: '    Dm  G', lyric: '' },
    { chords: '    C2  C9/E  F6(9)', lyric: '' },
    { chords: '    C2  C9/E  F6(9)', lyric: '' },
  ]},
  { type: 'part', label: '1ª Parte', num: 1, lines: [
    { chords: '    C2             C9/E         F6(9)', lyric: 'Somente em ti construirei a minha casa' },
    { chords: '    C2             C9/E         F6(9)', lyric: 'Somente em ti colocarei minha esperança' },
  ]},
  { type: 'prechorus', label: 'Pré-Refrão', lines: [
    { chords: '           Am7', lyric: 'Pois só em ti' },
    { chords: '                    G', lyric: "Minh'alma achou descanso" },
    { chords: ' C9/E  F', lyric: 'Só em  ti' },
    { chords: '     G            C2', lyric: 'Eu pude respirar' },
  ]},
  { type: 'chorus', label: 'Refrão', lines: [
    { chords: '    F              G', lyric: 'Em terra seca e sem caminhos' },
    { chords: '    Em             Am', lyric: 'Eu encontrei em ti a fonte' },
    { chords: '    Dm      G           C', lyric: 'Água viva que jorra sem cessar' },
    { chords: '    F              G              Am', lyric: 'Vem, Espírito, derrama sobre nós' },
  ]},
  { type: 'part', label: '2ª Parte', num: 2, lines: [
    { chords: '    C2             C9/E         F6(9)', lyric: 'Somente em ti encontro a minha paz' },
    { chords: '    C2             C9/E         F6(9)', lyric: 'Somente em ti descanso o coração' },
  ]},
  { type: 'bridge', label: 'Ponte', lines: [
    { chords: '    Am7       F', lyric: 'E se tudo passar' },
    { chords: '    C         G', lyric: 'Ainda assim serás meu chão' },
  ]},
];

window.SONG = SONG;
