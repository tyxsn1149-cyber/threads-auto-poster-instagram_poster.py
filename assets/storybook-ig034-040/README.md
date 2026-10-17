# ig034–ig040 絵本調リール修正（2026-10-18）

標準キャラクター参照を用い、内蔵image_genで各テーマの挿絵を生成。1本につき1枚の挿絵を3画面で共用し、既存の字幕を保持。生成り背景・茶色の文字・淡い色鉛筆と水彩の絵本調に統一。

仕様：1080×1920、15秒、30fps、H.264/AAC、3画面、上へめくる切替、オルゴール調BGM。投稿文・予定日時は変更しない。

再生成：`SNS_FONT=/path/to/NotoSansCJKjp-Regular.otf python generate_nextweek_reels.py`。必要環境はPillow、ffmpeg、日本語フォント。`SNS_IDS=ig034,ig035`で対象を限定できる。

## 生成プロンプト

共通：Use case: illustration-story. One landscape 3:2 illustration for a Japanese nursing Instagram reel. Use mandatory standard character identity reference. Match rounded animal faces, warm colored pencil and soft watercolor on cream paper, brown outlines, blush cheeks, established clothing colors. No readable text, no watermark, no human characters, no patient data. Single cohesive scene with generous cream margins.

### ig034
Penguin nurse in pale blue scrubs holding smartphone lowered before taking a hospital photo; senior calico cat in sage green scrubs and cream trousers gently points out blank medical chart on desk, cautious thoughtful expressions.

### ig035
Penguin nurse and panda colleague in beige scrubs and brown trousers looking thoughtfully at smartphone; small paper copies of blank phone screens evoke screenshot sharing, quiet staff lounge.

### ig036
Penguin nurse and pink scrub rabbit junior piecing together blank paper puzzle cards on a desk, realizing combined details reveal identity. Thoughtful gentle expressions.

### ig037
Penguin nurse giving concise report to senior calico cat in sage scrubs cream trousers, holding three blank memo cards, quiet hospital corridor, attentive communication.

### ig038
Pink scrub rabbit junior approaches penguin nurse with a memo and asks a question; penguin pauses work and listens warmly, staff room.

### ig039
Penguin nurse and beige scrub panda colleague checking a smartphone against an open reference book at wooden desk, thoughtful information verification.

### ig040
Penguin nurse carefully writing an educational post in notebook beside closed phone and reference books; calico senior in sage scrubs cream trousers reviews it together.

## 色の修正
ig035: penguin clothing corrected to pale blue scrubs and pale blue trousers; panda remains beige top and brown trousers.
ig039: panda trousers corrected to brown; beige top and penguin pale blue clothing preserved.
