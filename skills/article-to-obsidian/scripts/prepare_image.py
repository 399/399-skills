#!/usr/bin/env python3
"""Decode one captured image and make a small local vision preview (macOS)."""

import argparse
import base64
import json
import hashlib
import os
import tempfile
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
        return raw, image_format(raw), {}
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
    expected_bytes = payload.get('byteLength')
    if expected_bytes is not None and (type(expected_bytes) is not int or expected_bytes != len(data)):
        raise ValueError('浏览器提供的字节数与本地数据不一致')
    return data, ext, {k: payload[k] for k in ('noteId', 'index') if k in payload}


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
    data, ext, metadata = decode_source(args.source.expanduser().resolve(strict=True))
    if 'index' in metadata and metadata['index'] != args.index:
        raise ValueError('浏览器图片序号与 --index 不一致')
    root = args.capture_dir.resolve()
    originals, previews, checks, staging = [root / name for name in ('originals', 'previews', 'checks', '.staging')]
    for directory in (originals, previews, checks, staging):
        if not directory.resolve().is_relative_to(root):
            raise ValueError('输出子目录通过符号链接指向采集目录之外')
        directory.mkdir(parents=True, exist_ok=True)
    original = originals / f'{args.index:02d}.{ext}'
    preview = previews / f'{args.index:02d}-w540-q30.jpg'
    record = checks / f'{args.index:02d}.json'
    for existing in originals.glob(f'{args.index:02d}.*'):
        if existing != original or existing.is_symlink() or existing.read_bytes() != data:
            raise ValueError('该序号已有不同原图，拒绝覆盖；请检查文章目录和页码')
    if preview.is_symlink() or record.is_symlink():
        raise ValueError('输出路径是符号链接，拒绝写入')
    # All temporary files stay inside the explicitly selected capture directory.
    with tempfile.TemporaryDirectory(prefix=f'{args.index:02d}-', dir=staging) as pending:
        pending = Path(pending)
        candidate = pending / f'image.{ext}'
        candidate.write_bytes(data)
        # Decoding every frame catches malformed/truncated data, not only bad headers.
        try:
            from PIL import Image, ImageFile
        except ImportError as error:
            raise ValueError('完整解码校验需要 Pillow；请选择带 Pillow 的 Python 运行时，不降级为只检查文件头') from error
        ImageFile.LOAD_TRUNCATED_IMAGES = False
        with Image.open(candidate) as image:
            image.verify()
        with Image.open(candidate) as image:
            original_width, original_height = image.size
            frame_count = getattr(image, 'n_frames', 1)
            if original_width <= 0 or original_height <= 0:
                raise ValueError('图片尺寸无效')
            for frame in range(frame_count):
                image.seek(frame)
                image.load()
        width = min(540, original_width)
        pending_preview = pending / 'preview.jpg'
        subprocess.run([sips, '-s', 'format', 'jpeg', '-s', 'formatOptions', '30',
                        '--resampleWidth', str(width), str(candidate), '--out', str(pending_preview)],
                       capture_output=True, text=True, check=True)
        with Image.open(pending_preview) as image:
            image.load()
            if image.format != 'JPEG' or image.width != width:
                raise ValueError('预览图格式或尺寸不符合预期')
        # No final original is published until both source decoding and preview succeed.
        if not original.exists():
            os.link(candidate, original)  # Atomic create without replacing an existing file.
        os.replace(pending_preview, preview)
        result = {'index': args.index, 'noteId': metadata.get('noteId'),
                  'original': str(original), 'preview': str(preview),
                  'original_bytes': len(data), 'preview_bytes': preview.stat().st_size,
                  'sha256': hashlib.sha256(data).hexdigest(),
                  'format': ext, 'width': original_width, 'height': original_height,
                  'frames': frame_count, 'preview_width': width,
                  'download_status': 'validated', 'visually_read': False}
        pending_record = pending / 'record.json'
        pending_record.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        os.replace(pending_record, record)
        print(json.dumps(result, ensure_ascii=False))



if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'失败：{error}', file=sys.stderr)
        sys.exit(1)
