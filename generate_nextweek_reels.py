from pathlib import Path
from tempfile import TemporaryDirectory
from array import array
from PIL import Image, ImageDraw, ImageFont
import math
import subprocess
import wave
import os
from PIL import ImageOps

W, H = 1080, 1920
FONT_B = os.environ.get("SNS_FONT", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc")
FONT_R = os.environ.get("SNS_FONT", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
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
        ("「何を報告すればいいか\n分からない」", "そんなときは、\n最初の一言を決める。"),
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
    if post_id == "ig034":
        approved = Path("assets/ig034-approved") / f"ig034-{index}.png"
        ImageOps.fit(Image.open(approved).convert("RGB"), (W, H), method=Image.Resampling.LANCZOS).save(path)
        return
    # One original themed illustration per reel; three text layouts retain the script.
    im = Image.new("RGB", (W, H), (250, 246, 236))
    d = ImageDraw.Draw(im)
    ink = (73, 57, 47)
    d.text((90, 210), tag, font=font(31, True), fill=ink)
    d.text((990, 210), f"{index}/3", font=font(30), fill=ink, anchor="ra")
    # Wrap by measured character widths, including existing intentional newlines.
    def wrap(text, size, width):
        lines = []
        for para in text.split("\n"):
            line = ""
            for ch in para:
                if d.textlength(line + ch, font=font(size)) > width and line:
                    lines.append(line); line = ch
                else:
                    line += ch
            lines.append(line)
        return "\n".join(lines)
    title_font = fit(d, title, 880, 59, 44, False)
    title = wrap(title, title_font.size, 880)
    d.multiline_text((540, 325), title, font=title_font, fill=ink, anchor="ma", align="center", spacing=17)
    art = Image.open(Path("assets/storybook-ig034-040") / f"{post_id}.jpg").convert("RGB")
    art = ImageOps.contain(art, (960, 660), Image.Resampling.LANCZOS)
    im.paste(art, ((W-art.width)//2, 640+(660-art.height)//2))
    body = wrap(body, 40, 880)
    d.multiline_text((540, 1330), body, font=font(40), fill=ink, anchor="ma", align="center", spacing=16)
    d.line((90, 1710, 990, 1710), fill=(212, 200, 181), width=2)
    d.text((90, 1750), "看護師のための実務メモ", font=font(28), fill=ink)
    d.text((990, 1750), post_id, font=font(28), fill=ink, anchor="ra")
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
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-filter_complex_threads", "1"]
    for p in images:
        cmd += ["-loop", "1", "-t", "5", "-i", str(p)]
    cmd += ["-i", str(music), "-filter_complex",
        "[0:v]fps=30,format=yuv420p[v0];[1:v]fps=30,format=yuv420p[v1];[2:v]fps=30,format=yuv420p[v2];"
        "[v0][v1]xfade=transition=slideup:duration=0.5:offset=4.5[x1];"
        "[x1][v2]xfade=transition=slideup:duration=0.5:offset=9.0,tpad=stop_mode=clone:stop_duration=1[v]",
        "-map", "[v]", "-map", "3:a", "-t", "15", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(output)]
    subprocess.run(cmd, check=True)


with TemporaryDirectory() as temp:
    work = Path(temp)
    music = work / "musicbox.wav"
    make_music(music)
    for post_id, (tag, content) in POSTS.items():
        if os.environ.get("SNS_IDS") and post_id not in os.environ["SNS_IDS"].split(","):
            continue
        render(post_id, tag, content, work, music)
        print(f"generated {post_id}")
