#!/bin/zsh
# サイト画像の差し替え: 元フォルダの hero-expansion / service-email / service-line / service-video / service-ai (.png か .jpg) を
# assets に WebP(1536・768)+JPG で書き出す。使い方: tools/update_images.sh /path/to/images-v2
set -e
SRC="$1"; [ -d "$SRC" ] || { echo "フォルダが無い: $SRC"; exit 1; }
cd "$(dirname "$0")/../assets"
for n in hero-expansion service-email service-line service-video service-ai; do
  f=""; for ext in png jpg jpeg; do [ -f "$SRC/$n.$ext" ] && f="$SRC/$n.$ext" && break; done
  [ -n "$f" ] || { echo "見つからない: $n"; exit 1; }
  cwebp -quiet -q 82 "$f" -o "$n.webp"
  cwebp -quiet -q 80 -resize 768 0 "$f" -o "$n-768.webp"
  sips -s format jpeg -s formatOptions 82 "$f" --out "$n.jpg" >/dev/null
  echo "$n: $(sips -g pixelWidth -g pixelHeight "$f" | awk '/pixel/{printf "%s ", $2}') → webp $(stat -f%z "$n.webp")B / 768 $(stat -f%z "$n-768.webp")B / jpg $(stat -f%z "$n.jpg")B"
done
