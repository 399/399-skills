# Neo 正文与评论读取

先应用当前安装的 `browseros-neo` skill。发现本次工具名称和参数；连接重建后先列标签，再根据来源 URL 与任务组确认页面。使用本次列表的 `pageId`（不是猜测 `.id`），工具返回值可能包装在 `structuredContent.value`，页面 evaluate 还可能再包装一层 `{page,value}`；大结果读取返回路径，不重复拉取或输出整个 DOM。

`page.read()` 取得正文，`page.snapshot()` 取得控件。页面可能混有推荐流；只提取当前笔记容器，不能把推荐文章并入正文。来源保留原始用户链接、标题和作者；无法取得发布日期时不要拿采集日冒充发布日期。

## 小红书评论完整性

1. 检查 `.comments-container`，记录页面标示的总数，识别 `.comment-item` 以及 `.parent-comment` 分组。先展开正文中的“全文”，再展开评论“全文”、`.show-more`、更多子回复。
2. 用 snapshot 中实际 ref 点击，每次按返回变化重新观察；加载未结束时等待对应控件或内容变化。不点发表“回复”、点赞、收藏或关注。
3. 实测有“展开 6 条回复”一次只加载 5 条，随后变成“展开更多回复”。点过一次不能算该线程已完整。
4. 如果 snapshot 给 `.show-more` 一个无名称的 generic ref，可通过 evaluate 给**已经定位的展开控件**临时补 `aria-label`，重新 snapshot 后按 ref 点击。只补可访问名称，不修改正文，不将“回复”输入按钮误标为展开。
5. 滚动实际评论滚动容器（测试中为 `.note-scroller`），每次等待新增内容。不要只滚动页面主体。到 `THE END` 或明确末尾后，再检查是否仍有全文/子回复展开项。
6. 用 comment ID 去重，保存父线程及明确的回复对象。测试中 `.parent-comment` 第一条 `.comment-item` 可代表该组根评论；嵌套内容中的“回复 某人”还需保留，不能把同组回复都当作直接回应根评论。
7. 作者标记的 DOM 类名可能变化；结合页面可见“作者”标志及原帖作者主页身份核对，不能依赖一个失效的 `.author-tag` 选择器。点赞数不是回复数，显示昵称相同也不保证同一账号。
8. 末尾标志、展开控件清空、实际唯一评论数与标示数匹配，共同支持“网页可见范围已读完”。若总数不匹配、加载失败、存在虚拟列表或需要登录，应保留已读数据并报告缺口，不承诺读到平台隐藏或删除内容。

15 图测试中，初始只显示部分顶层评论与每组第一条回复；依次展开，再滚动 `.note-scroller` 后取得 38 条唯一评论，页面也标示 38 条，剩余 `.show-more` 为 0，并出现 `THE END`。2026-10-13 复测时可见讨论增至 39 条唯一评论，仍为零剩余展开控件且出现 `THE END`；新增观点随本次内容整理。每次都重新核对，不能沿用旧数量。这是测试的证据组合，不是其他帖子的固定数量或永远有效的选择器。

## 浏览器内 OCR（可选）

仅在确有文字转写需要时使用，照片仍按 [image-vision.md](image-vision.md) 视觉阅读。

在自己创建的独立 `about:blank` 页加载：

```javascript
await page.evaluate(() => {
  window.ocrJob = {status:'loading library'};
  const script = document.createElement('script');
  script.src = 'https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js';
  script.onload = async () => {
    try {
      window.ocrJob.status = 'loading languages';
      window.ocrWorker = await Tesseract.createWorker('chi_sim+eng', 1, {
        logger: message => { window.ocrJob.progress = message; }
      });
      window.ocrJob.status = 'ready';
    } catch (error) {
      window.ocrJob = {status:'error',error:String(error)};
    }
  };
  script.onerror = () => { window.ocrJob = {status:'error',error:'script load failed'}; };
  document.head.append(script);
});
```

初始化与识别分次调用，读取状态，不占住单次 run 超过 30 秒。只对当前文章实际取得的图片 URL 或已获准处理的图片运行 `worker.recognize`；保存页码、文本、confidence 及错误到用户采集目录。总数与逐图状态匹配后再使用结果。confidence 不是正确率保证；尤其核对小数、单位、否定词和正文冲突。结束时可 terminate 自己创建的 worker，避免持续占用资源。
