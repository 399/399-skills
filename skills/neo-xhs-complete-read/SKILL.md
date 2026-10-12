---
name: neo-xhs-complete-read
description: "读取小红书正文、按顺序检查配图，并展开评论回复；记录覆盖范围和识别疑点。"
---

## 采集目录（开始前）

必须使用用户提供的本地采集根目录，优先复用当前对话中已明确指定的路径。用户未提供时先询问：“原图、预览图和采集临时文件放在哪个本地目录？建议选不参与同步的位置。”在回答前不下载或落盘采集材料，不擅自使用项目 work/tmp、系统临时目录、Downloads 或 Obsidian 附件目录。原图、裁切、OCR 和检查记录只进该目录下的文章子目录；最终 Markdown 不嵌入采集日志，仅在用户要求入库时带上必要配图。

本 skill 负责小红书完整读取。生成 Obsidian 收藏笔记时，同时使用已安装的 `article-to-obsidian` skill；按其规定分开核心摘要（作者观点）、评论讨论、疑点与核查、原文留存（作者/评论分开）。

## Steps
1. Call the mark_skill_run tool with name: neo-xhs-complete-read so this run is recorded.
2. 先用 browser.pages.list() 查找本任务页面，必要时 browser.open(用户提供的链接)。用 page.read() 读取正文，用 page.snapshot() 观察实际页面和交互控件，保留来源与作者。
3. 用 page.evaluate() 在当前笔记的轮播容器内枚举 .swiper-slide:not(.swiper-slide-duplicate) img，保持页序并去重。读取 currentSrc || src；lazy 图片的 currentSrc 可能为空，不要把空字符串当作原图。按本次页面结构核对图片数量。
4. 优先让视觉模型读取逐张原图或清晰的分块截图。若工具返回了截图但模型输入明确移除了图片，不得声称看过像素，也不得用正文猜图片内容。
5. 截图附件未进入模型输入时，通过 Neo 页面实际取得的图片 URL 下载原图，保存到用户指定目录，再用本地 `view_image` 视觉读取。实测一部分原始 WebP 可直接显示；较大图和宽 900、质量 60 的 JPEG 仍失败，但宽 540 像素、JPEG 质量 30 的预览成功。数字、单位和小字从原图局部裁切，以更高质量再次视觉核对；不能只把低清预览放大。具体 Neo fetch/FileReader、本地解码脚本和 sips 裁切步骤见 `article-to-obsidian` 的 `references/image-vision.md`。独立使用本 skill 时也必须遵守目录约定；每张都要实际看见像素，文件成功或 OCR 成功不等于读图成功。
6. 文字配图可以用 Neo 内本地运行的 Tesseract.js 备用 OCR。在独立 about:blank 标签中载入 https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js，用 Tesseract.createWorker('chi_sim+eng',1,{logger:...}) 初始化。把初始化 Promise 和状态保存在 window 上，分次读取状态，避免超过单次 run 的 30 秒。
7. 将观察到的原图 URL 依次交给浏览器内 OCR worker.recognize()。计算在浏览器内完成，不把图片提交给云端 OCR 服务。每张记录页码、文本、识别置信度；非文字图表仍需视觉模型分析，OCR 不能替代。
8. 交叉核对 OCR 的数字、单位、否定词及与正文重复的段落，尤其防止 4.5 被识别成 45。低置信度或无法核对的位置明确标记，不能补写猜测。先核对全部图片的成功状态，再生成摘要。
9. 用 page.snapshot() 找到当前评论区的展开全文、展开回复、更多回复和加载更多控件，按 ref 用 page.click() 逐层展开，每次再观察状态。滚动评论容器，检查末尾标志和可见数量。不要点击用于发表回复的“回复”按钮。
10. 用 page.evaluate() 提取评论父子结构和当前已展开的内容，区分原作者回应、读者实践、分歧与修正。“展开 N 条”之后可能还有“展开更多回复”；须继续点击，并滚动实际评论容器（实测为 .note-scroller）。用评论 ID 去重，核对实际唯一评论数、空的展开控件列表及 THE END 等末尾证据；记录网页可见范围，不宣称获取平台不可见评论。
11. 输出时分开组织忠实摘要、原文留存信息、评论讨论、疑点与核查；摘要不混入 AI 反驳，评论保留观点来源及回复关系。缺图、未展开或加载失败必须如实列明。

## Learned from past runs
- 已在一个五图两评论的帖子上跑通浏览器内中文 OCR；封面装饰字和个别数字仍可能误识别。
- 本机 Swift Vision OCR 返回 nilError；不应重复调用同一路径作为默认兜底。
- 15 图测试实际逐张视觉读取成功：原始 WebP → 必要时宽 540、质量 30 的 JPEG 预览 → 原图局部裁切确认小字。更早的截图和宽 900、质量 60 的版本曾被网关移除，不能笼统写成“缩小 JPEG 无效”，也不能把这组参数当普遍保证。
- 同一测试展开回复并滚动到底后读到 38 条唯一评论，与页面总数匹配，且无剩余展开控件、出现 THE END。该证据只适用于当次网页可见范围。
- 页面显示的数字可能是点赞数而不是回复数，须根据控件和层级确认。
