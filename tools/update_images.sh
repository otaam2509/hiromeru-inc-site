#!/bin/zsh
# サイト画像の差し替え: 元フォルダの hero-workplace-v2 / service-*-photo-v2 (.png か .jpg) を。次に差し替えるときはファイル名を v3 等に変えてキャッシュを避ける
# assets に WebP(1536・768)+JPG で書き出す。使い方: tools/update_images.sh /path/to/images-v2
set -e
SRC="$1"; [ -d "$SRC" ] || { echo "フォルダが無い: $SRC"; exit 1; }
cd "$(dirname "$0")/../assets"
for n in hero-workplace-v2 service-email-photo-v2 service-line-photo-v2 service-video-photo-v2 service-ai-photo-v2; do
  f=""; for ext in png jpg jpeg; do [ -f "$SRC/$n.$ext" ] && f="$SRC/$n.$ext" && break; done
  [ -n "$f" ] || { echo "見つからない: $n"; exit 1; }
  cwebp -quiet -q 82 "$f" -o "$n.webp"
  cwebp -quiet -q 80 -resize 768 0 "$f" -o "$n-768.webp"
  sips -s format jpeg -s formatOptions 82 "$f" --out "$n.jpg" >/dev/null
  echo "$n: $(sips -g pixelWidth -g pixelHeight "$f" | awk '/pixel/{printf "%s ", $2}') → webp $(stat -f%z "$n.webp")B / 768 $(stat -f%z "$n-768.webp")B / jpg $(stat -f%z "$n.jpg")B"
done
