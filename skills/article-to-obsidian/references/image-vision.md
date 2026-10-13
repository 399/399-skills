# 图片视觉读取：本次实测成功路径

## 成功证据与适用边界

2026-10-12 的小红书 15 图帖子测试中：Neo 截图返回了附件，但模型输入提示图片被网关移除；通过页面获取原图并本地解码后，一部分 WebP 可由 `view_image` 直接看到。较大图片依然被移除，宽 900 像素、JPEG 质量 60 的版本也失败；**宽 540 像素、JPEG 质量 30** 的预览成功显示。对第 11 图的保温档位，再从原图裁切文字区域，实际看清了 `40–45–50–55℃`，识别出与正文三档表述的差异。

因此已实测的视觉链路是：**Neo 页面实际图片 → 用户指定目录内的原图 → 本地视觉读取 → 必要时小预览 → 原图局部裁切复核。** 本次没有依赖 OCR 来推断照片。不能保证缩图参数解决所有网关问题，也不能仅凭文件大小诊断原因。

2026-10-13 在线复测：目标笔记 ID、state 图片数、DOM 轮播数与界面总数一致（15 张）；全部首轮下载成功，通过完整解码、尺寸、字节数和 SHA-256 校验，15 张静态画面均通过本地预览实际视觉阅读，第 11 图另裁切核对。实际失败补采没有触发，仍只有合成测试证据；CDN 地址重写仍未启用或验证。

当前约定只验收静态图文。Live Photo、GIF 等只阅读静态画面；发现动态属性时记为范围外跳过，不要求提取动态流、播放或抽帧。历史复测曾额外抽看 Live Photo，不是后续采集的必做步骤。图片文件的完整解码校验属于文件完整性检查，不等于动态内容分析。

## 1. 取得真实图片

- 开始前必须已有用户指定的本地采集根目录；没有就先询问，禁止默认写入项目临时目录。
- 先尝试清晰截图或原图视觉读取。图片确已可见、信息可读时，不必为了流程重复下载。
- 先按 [image-inventory.md](image-inventory.md) 取得已核对笔记 ID 的页面数据 `imageList`，再与当前笔记 DOM 轮播及可见总数交叉核对。页面数据缺失才退回 DOM。使用页面提供的实际有效 URL，不猜 CDN 路径、不修改签名或绕过访问限制。每张保留原帖序号；仅消除 DOM 轮播克隆，不因内容重复而合并原帖页码。
- 原生下载可用时优先使用。也可在已打开页面中执行 `page.evaluate`，让浏览器取回已展示图片的字节并交回本地，属于内容分析，不是绕过媒体显示限制。不要用生图工具来读图。

浏览器下载示例（使用已核对清单中的单张图片，不再临时按 DOM 下标重新取链接）：

```javascript
const result = await page.evaluate(async item => {
  // item 仅含 noteId、index、清单中核对过的 url；不传 Cookie。
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const response = await fetch(item.url, {signal: controller.signal});
    if (response.status !== 200) throw new Error(`图片响应 ${response.status}`);
    const blob = await response.blob();
    if (!blob.size || !blob.type.startsWith('image/')) throw new Error('空响应或非图片');
    const length = response.headers.get('content-length');
    // 压缩传输的 Content-Length 可能不是解压后长度；只在可比较时核对。
    if (!response.headers.get('content-encoding') && length !== null &&
        Number(length) !== blob.size) throw new Error('响应长度不一致');
    const data = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error('读取图片失败'));
      reader.readAsDataURL(blob);
    });
    return {noteId:item.noteId, index:item.index, byteLength:blob.size, type:blob.type, data};
  } finally { clearTimeout(timer); }
}, selectedItem);
```

清单核对后最多并发 2 张，每张最多 3 次尝试，只重试失败项。一次 run 内做有界尝试，错误保存到本地清单；超时和临时网络故障可补试，认证或验证码交由用户处理。403 或链接过期时先重新读取同一笔记的有效链接，不持续请求失效地址。小图直接完整重下，不使用未经验证的 Range 追加续传。跨调用保留原帖序号，不能把失败条目删掉再重排。

每个 Neo `run` 有约 30 秒上限；按批处理，不对未完成任务用无限等待。不要把 Base64 打印到聊天中。浏览器工具可能自动把大结果写入其服务管理的 `tool-output` 缓存，这不是 agent 可指定的采集目录；从返回的**确切路径**解码到用户目录，不枚举别的会话文件，也不把该缓存当长期档案。若用户要求连工具缓存也必须禁止或更改，应说明工具能力限制，先解决再采集。

## 2. 本地解码与小预览

附带的 [scripts/prepare_image.py](../scripts/prepare_image.py) 支持原图文件，或包含 `{type, data: "data:image/...;base64,..."}` 的 Neo JSON 输出（包括 untrusted 内容标记包装）。它核对图片序号、浏览器给出的字节数、实际文件头和 MIME，并使用 Pillow 完整解码每一帧；再用 macOS 的 `sips` 生成宽度不超过 540 像素、JPEG 质量 30 的预览。原图不会重编码。

必须选择带 Pillow 的 Python 运行时；本机系统 Python 不一定有 Pillow，可使用当前应用提供的依赖运行时。缺少解码库时明确报错，不降级为只检查文件头。脚本不联网，不选择默认目录，不覆盖不同内容的已有原图。所有中间文件放在用户文章目录内的 `.staging/`，校验和预览都通过后才以原子操作发布原图、预览和 `checks/序号.json`。

命令中的采集路径必须替换为用户已指定根目录下的当前文章子目录；不是让 agent 照抄一个默认路径：

```sh
python3 /实际技能路径/scripts/prepare_image.py \
  --source '/工具本次返回的确切文件或已有原图' \
  --capture-dir '/用户指定根目录/站点-文章ID' \
  --index 2
```

返回 `original`、`preview`、尺寸、帧数、字节数、SHA-256 及 `download_status: validated`；SHA-256 用于本地一致性和重复检查，不证明服务器给的是作者无损原图。逐图记录只保存技术校验，`visually_read` 始终为 false；人工视觉状态另记在本地清单，不能由下载脚本宣告。先读取原图；被移除或过大时读小预览。Codex 工具调用示例：

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


## 5. 完整性与补采

本地图片清单保留 `noteId`、预期总数、每张 `index`、实际地址、`downloadStatus`（pending/failed/validated）、尝试次数、错误、校验记录路径、视觉状态和配图选择理由。不要保存浏览器 Cookie 或整份页面初始状态，也不要把带签名的地址提交到公共仓库。

- 重跑时先检查成功项的校验记录，并重新比对文件的 SHA-256；一致才跳过重复下载。脚本再次执行会重新校验同一份数据，不覆盖不同内容。只有记录但文件缺失、哈希不同，都不能直接跳过。
- 下载失败与视觉未读是两种待办：前者补采，后者使用已有原图进行预览或裁切，不重新下载所有图。
- 文件损坏或冲突时，保留旧文件并在当前用户目录中换一个明确的重试子目录；不要让 agent 为了绕开冲突偷偷改原帖序号。
- 所有预期序号均有有效文件及独立视觉状态，才能宣称全部静态配图已读；已知动态配图仅查看静态画面时另注明范围。必要配图复制到最终输出时复核字节或哈希、相对引用与总大小；不要带上 `.staging`、`checks` 和原始清单。
