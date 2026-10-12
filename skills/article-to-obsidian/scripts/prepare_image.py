#!/usr/bin/env python3
"""Decode one captured image and make a small local vision preview (macOS)."""

import argparse
import base64
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


def image_format(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'
    if data.startswith(b'\xff\xd8\xff'):
        return 'jpg'
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'webp'
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'
    if data[:4] in (b'II*\x00', b'MM\x00*'):
        return 'tiff'
    raise ValueError('不支持或无效的图片；支持 PNG/JPEG/WebP/GIF/TIFF')


def decode_source(path):
    raw = path.read_bytes()
    try:
        return raw, image_format(raw)
    except ValueError:
        pass
    text = raw.decode('utf-8')
    start = text.find('{')
    if start < 0:
        raise ValueError('不是图片或包含图片 data URL 的 JSON')
    payload, _ = json.JSONDecoder().raw_decode(text[start:])
    # Only known tool wrappers; never recursively search arbitrary page content.
    for key in ('structuredContent', 'value', 'value'):
        if isinstance(payload, dict) and 'data' not in payload and key in payload:
            payload = payload[key]
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), str):
        raise ValueError('JSON 缺少图片 data 字段')
    match = re.fullmatch(r'data:image/(png|jpeg|jpg|webp|gif|tiff);base64,([A-Za-z0-9+/=\s]+)', payload['data'])
    if not match:
        raise ValueError('只接受受支持的 base64 图片 data URL')
    data = base64.b64decode(re.sub(r'\s+', '', match.group(2)), validate=True)
    ext = image_format(data)
    declared = {'jpeg': 'jpg'}.get(match.group(1), match.group(1))
    if ext != declared:
        raise ValueError('图片 MIME 与实际文件格式不一致')
    return data, ext


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--capture-dir', type=Path, required=True,
                        help='用户已指定根目录下的文章子目录；不得由 agent 擅自默认')
    parser.add_argument('--index', type=int, required=True, help='原帖图片序号，从 1 开始')
    args = parser.parse_args()
    if args.index < 1:
        parser.error('--index 必须大于 0')
    if not args.capture_dir.is_absolute():
        parser.error('--capture-dir 必须是用户指定的绝对路径')
    sips = shutil.which('sips')
    if not sips:
        raise ValueError('需要 macOS sips；当前环境不可用，未自动安装替代工具')
    data, ext = decode_source(args.source.expanduser().resolve(strict=True))
    root = args.capture_dir.resolve()
    originals = root / 'originals'
    previews = root / 'previews'
    for directory in (originals, previews):
        if not directory.resolve().is_relative_to(root):
            raise ValueError('输出子目录通过符号链接指向采集目录之外')
        directory.mkdir(parents=True, exist_ok=True)
    original = originals / f'{args.index:02d}.{ext}'
    preview = previews / f'{args.index:02d}-w540-q30.jpg'
    for existing in originals.glob(f'{args.index:02d}.*'):
        if existing != original or existing.is_symlink() or existing.read_bytes() != data:
            raise ValueError('该序号已有不同原图，拒绝覆盖；请检查文章目录和页码')
    if preview.is_symlink():
        raise ValueError('预览路径是符号链接，拒绝写入')
    if not original.exists():
        with original.open('xb') as output:
            output.write(data)
    info = subprocess.run([sips, '-g', 'pixelWidth', str(original)],
                          text=True, capture_output=True, check=True).stdout
    width_match = re.search(r'pixelWidth:\s*(\d+)', info)
    if not width_match:
        raise ValueError('sips 无法读取有效图片宽度；原图已保留')
    width = min(540, int(width_match.group(1)))
    subprocess.run([sips, '-s', 'format', 'jpeg', '-s', 'formatOptions', '30',
                    '--resampleWidth', str(width), str(original), '--out', str(preview)],
                   capture_output=True, text=True, check=True)
    print(json.dumps({'original': str(original), 'preview': str(preview),
                      'original_bytes': original.stat().st_size,
                      'preview_bytes': preview.stat().st_size,
                      'preview_width': width,
                      'visually_read': False}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'失败：{error}', file=sys.stderr)
        sys.exit(1)
