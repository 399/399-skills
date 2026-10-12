# 图片视觉读取：本次实测成功路径

## 成功证据与适用边界

2026-10-12 的小红书 15 图帖子测试中：Neo 截图返回了附件，但模型输入提示图片被网关移除；通过页面获取原图并本地解码后，一部分 WebP 可由 `view_image` 直接看到。较大图片依然被移除，宽 900 像素、JPEG 质量 60 的版本也失败；**宽 540 像素、JPEG 质量 30** 的预览成功显示。对第 11 图的保温档位，再从原图裁切文字区域，实际看清了 `40–45–50–55℃`，识别出与正文三档表述的差异。

因此成功链路是：**Neo 页面实际图片 → 用户指定目录内的原图 → 本地视觉读取 → 必要时小预览 → 原图局部裁切复核。** 本次没有依赖 OCR 来推断照片。不能保证缩图参数解决所有网关问题，也不能仅凭文件大小诊断原因。

## 1. 取得真实图片

- 开始前必须已有用户指定的本地采集根目录；没有就先询问，禁止默认写入项目临时目录。
- 先尝试清晰截图或原图视觉读取。图片确已可见、信息可读时，不必为了流程重复下载。
- 需要本地分析时，通过已授权的 Neo 浏览器取得当前页面真正使用的图片 URL；不猜 CDN 路径、不修改签名或绕过访问限制。对于小红书，顺序枚举当前笔记内 `.swiper-slide:not(.swiper-slide-duplicate) img`，读取 `currentSrc || src`。以轮播位置保存；仅消除 DOM 轮播克隆，不因内容重复而丢失原帖页码。
- 原生下载可用时优先使用。也可在已打开页面中执行 `page.evaluate`，让浏览器取回已展示图片的字节并交回本地，属于内容分析，不是绕过媒体显示限制。不要用生图工具来读图。

经过实测的浏览器代码，按实际 DOM 修改容器，并从本次 `browser.pages.list()` 取得 `pageId`：

```javascript
// evaluate 可能返回 {page, value}，大返回值可能为 {page, path, writtenToFile:true}。
const result = await page.evaluate(async index => {
  const nodes = Array.from(document.querySelectorAll(
    '.swiper-slide:not(.swiper-slide-duplicate) img'
  ));
  const node = nodes[index];
  if (!node) throw new Error('图片序号不存在');
  const url = node.currentSrc || node.src;
  if (!url) throw new Error('图片 URL 为空');
  const response = await fetch(url);
  if (!response.ok) throw new Error(`图片响应 ${response.status}`);
  const blob = await response.blob();
  if (!blob.type.startsWith('image/')) throw new Error('响应不是图片');
  const data = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('读取图片失败'));
    reader.readAsDataURL(blob);
  });
  return {type: blob.type, data};
}, imageIndex);
```

每个 Neo `run` 有约 30 秒上限；按批处理，不对未完成任务用无限等待。不要把 Base64 打印到聊天中。浏览器工具可能自动把大结果写入其服务管理的 `tool-output` 缓存，这不是 agent 可指定的采集目录；从返回的**确切路径**解码到用户目录，不枚举别的会话文件，也不把该缓存当长期档案。若用户要求连工具缓存也必须禁止或更改，应说明工具能力限制，先解决再采集。

## 2. 本地解码与小预览

附带的 [scripts/prepare_image.py](../scripts/prepare_image.py) 支持原图文件，或包含 `{type, data: "data:image/...;base64,..."}` 的 Neo JSON 输出（包括 untrusted 内容标记包装）。它保留原图，使用 macOS 的 `sips` 生成宽度不超过 540 像素、JPEG 质量 30 的预览；不联网，不选择默认目录，不覆盖不同内容的已有文件。

命令中的采集路径必须替换为用户已指定根目录下的当前文章子目录；不是让 agent 照抄一个默认路径：

```sh
python3 /实际技能路径/scripts/prepare_image.py \
  --source '/工具本次返回的确切文件或已有原图' \
  --capture-dir '/用户指定根目录/站点-文章ID' \
  --index 2
```

返回 `original` 和 `preview` 的绝对路径。先读取原图；被移除或过大时读小预览。Codex 工具调用示例：

```javascript
const result = await tools.view_image({path: actualAbsoluteImagePath});
image(result.image_url);
```

模型输入必须确实出现图片像素。如果显示 `[Attached image removed by gateway due to context size limits]`，该次读取不算成功；有文件、有 `image_url` 或工具成功状态均不足为证。

## 3. 检查照片与标注

逐图记录在本地：主体、部件位置、动作或步骤、箭头与文字指向、上下或左右对比，以及仍看不清的地方。不要只抄文字。例如：杯盖内外结构、旧壶与新杯在行李箱内的布局，都是 OCR 无法完整保留的信息。

预览图适合整体理解；数字、单位、否定词、型号、密集标注必须能读清。读不清时从原图裁切，不是把低清缩略图放大后猜测。测试中用到的 macOS 命令：

```sh
sips -s format jpeg -s formatOptions 75 \
  --cropToHeightWidth 290 1080 --cropOffset 60 0 \
  '/用户指定目录/原图.webp' \
  --out '/用户指定目录/局部文字.jpg'
```

这里的尺寸和坐标仅对应那张测试图片；针对实际图片确定区域，再用 `view_image` 检查裁切结果。高密度长图按原图区域分块，保留少量重叠与原图序号。分析用的小预览不自动作为最终配图；入文时选可读、体积合适的原图或压缩版本。

## 4. 失败与 OCR 备用

- 直接读取、540 像素预览及针对性局部裁切仍无法显示或读清时，停止重复转换；准确说明哪些图或区域未完成，不声称视觉读取完整。
- OCR 可辅助转写文字，但不能替代照片、图表、箭头和空间关系的理解。纯文字图 OCR 成功，也要说明关键数字的复核情况。
- 需要 OCR 时，可按 [neo-reading.md](neo-reading.md) 在 Neo 的独立空白页运行 Tesseract.js；图像识别计算在浏览器内执行，不提交第三方 OCR 接口。库和语言文件的加载仍会访问 CDN，不能宣称整个流程完全离线。
- 本机过去的 Swift Vision OCR 返回过 `nilError`，不再把无变化地重试这一路径当默认兜底。不要未经授权引入远程图像分析服务。
