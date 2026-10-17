from pathlib import Path
from tempfile import TemporaryDirectory
from array import array
from PIL import Image, ImageDraw, ImageFont
import math
import subprocess
import wave

W, H = 1080, 1920
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_R = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
BG = (246, 248, 251)
NAVY = (25, 46, 68)
TEXT = (45, 57, 70)
SUB = (92, 105, 120)
ACCENT = (205, 226, 222)
LINE = (220, 226, 233)

POSTS = {
    "ig034": ("SNSリテラシー 01", [
        ("患者さんが映っていなければ\n院内写真を載せても大丈夫？", "実は、そうとは限りません。"),
        ("写真の中を確認", "患者氏名 / 薬剤名 / ネームバンド\n電子カルテ / ホワイトボード / 病室番号"),
        ("投稿前の3チェック", "① 職場の撮影・SNSルール\n② 患者情報が写っていないか\n③ 組み合わせから特定できないか\n\n迷ったら投稿しない。"),
    ]),
    "ig035": ("SNSリテラシー 02", [
        ("24時間で消えるから大丈夫？", "ストーリーズでも、\n情報漏えいのリスクはなくなりません。"),
        ("こんな考え方は危険", "「鍵アカだから」\n「親しい友達だけだから」\n「すぐ消えるから」\n\nスクリーンショットや転載は防げません。"),
        ("公開範囲ではなく\n“投稿内容”で判断する", "院内・患者情報は\n投稿しないことを基本に。"),
    ]),
    "ig036": ("SNSリテラシー 03", [
        ("「名前を書いてないから大丈夫」", "本当にそうでしょうか？"),
        ("一つでは匿名でも…", "「80代」\n「珍しい病気」\n「昨日緊急搬送」\n「○○病棟」"),
        ("情報を組み合わせると\n本人が推測できることがあります", "患者エピソードを\nSNSのネタにしない。"),
    ]),
    "ig037": ("報告・相談 01", [
        ("「何を報告すればいいか分からない」", "そんなときは、\n最初の一言を決める。"),
        ("まず伝える3つ", "① 何が起きたか\n② 緊急度\n③ 何を相談したいか"),
        ("結論を先に", "「血圧が低下しています。\n今すぐ診察をお願いしたいです」"),
    ]),
    "ig038": ("報告・相談 02", [
        ("「忙しそうだから、あとにしよう」", "患者安全に関わる相談でも\n同じですか？"),
        ("声をかけるなら", "「○○について判断に迷っています。\n今、相談できますか？」\n\n急ぐなら緊急度も伝える。"),
        ("相手への気遣いと\n必要な相談は両立できます", "重要な相談を後回しにしない。"),
    ]),
    "ig039": ("医療リテラシー", [
        ("「SNSで見たんですが、\nこれ本当ですか？」", "患者さんから聞かれたら？"),
        ("まず確認する3つ", "① 誰が発信した？\n② 根拠は示されている？\n③ 情報は新しい？"),
        ("すぐに正解・不正解を決めない", "公的機関や一次情報を確認する。"),
    ]),
    "ig040": ("医療情報発信", [
        ("看護師だから\n医療情報を自由に発信していい？", "専門職だからこそ確認が必要です。"),
        ("投稿前に3チェック", "① 根拠はあるか\n② 最新情報か\n③ 誤解を招く表現ではないか"),
        ("「分かりやすい」と\n「言い切る」は別", "正確さを失わず\n分かりやすく伝える。"),
    ]),
}


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)


def fit(draw, text, max_width, start, minimum, bold):
    size = start
    while size >= minimum:
        f = font(size, bold)
        box = draw.multiline_textbbox((0, 0), text, font=f, spacing=int(size * 0.28), align="center")
        if box[2] - box[0] <= max_width:
            return f
        size -= 2
    return font(minimum, bold)


def slide(path, post_id, tag, index, title, body):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((76, 88, 430, 150), radius=30, fill=ACCENT)
    d.text((102, 102), tag, font=font(29, True), fill=NAVY)
    d.text((982, 108), f"{index}/3", font=font(28, True), fill=SUB, anchor="ra")

    d.rounded_rectangle((435, 330, 645, 540), radius=44, fill=(255,255,255), outline=LINE, width=4)
    d.ellipse((510, 395, 570, 455), outline=NAVY, width=7)
    d.line((540, 455, 540, 486), fill=NAVY, width=7)
    d.line((512, 486, 568, 486), fill=NAVY, width=7)

    tf = fit(d, title, 900, 76, 46, True)
    d.multiline_text((540, 680), title, font=tf, fill=NAVY, anchor="ma", spacing=18, align="center")
    box = d.multiline_textbbox((0, 0), title, font=tf, spacing=18, align="center")
    y = 720 + (box[3] - box[1])
    d.rounded_rectangle((340, y, 740, y + 10), radius=5, fill=ACCENT)

    bf = fit(d, body, 860, 49, 34, False)
    d.multiline_text((540, y + 110), body, font=bf, fill=TEXT, anchor="ma", spacing=22, align="center")

    d.line((78, 1740, 1002, 1740), fill=LINE, width=3)
    d.text((78, 1790), "看護師のための実務メモ", font=font(30, True), fill=SUB)
    d.text((1002, 1790), post_id, font=font(28, True), fill=SUB, anchor="ra")
    im.save(path, "PNG")


def make_music(path):
    rate = 44100
    duration = 15
    notes = [659.25, 783.99, 880.00, 783.99, 698.46, 659.25, 587.33, 659.25]
    samples = array('h')
    for n in range(rate * duration):
        t = n / rate
        freq = notes[int(t / 0.5) % len(notes)]
        local = t % 0.5
        env = math.exp(-5 * local)
        value = (0.10 * math.sin(2 * math.pi * freq * t) + 0.035 * math.sin(4 * math.pi * freq * t)) * env
        samples.append(int(max(-1, min(1, value)) * 32767))
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(samples.tobytes())


def render(post_id, tag, content, work, music):
    images = []
    for i, (title, body) in enumerate(content, 1):
        p = work / f"{post_id}-{i}.png"
        slide(p, post_id, tag, i, title, body)
        images.append(p)

    output = Path(f"{post_id}-reel-15s.mp4")
    cmd = ["ffmpeg", "-y"]
    for p in images:
        cmd += ["-loop", "1", "-t", "5", "-i", str(p)]
    cmd += ["-i", str(music), "-filter_complex",
        "[0:v]fps=30,format=yuv420p[v0];[1:v]fps=30,format=yuv420p[v1];[2:v]fps=30,format=yuv420p[v2];"
        "[v0][v1]xfade=transition=slideup:duration=0.5:offset=4.5[x1];"
        "[x1][v2]xfade=transition=slideup:duration=0.5:offset=9.0,tpad=stop_mode=clone:stop_duration=1[v]",
        "-map", "[v]", "-map", "3:a", "-t", "15", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "33", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "40k", "-movflags", "+faststart", str(output)]
    subprocess.run(cmd, check=True)


with TemporaryDirectory() as temp:
    work = Path(temp)
    music = work / "musicbox.wav"
    make_music(music)
    for post_id, (tag, content) in POSTS.items():
        render(post_id, tag, content, work, music)
        print(f"generated {post_id}")
