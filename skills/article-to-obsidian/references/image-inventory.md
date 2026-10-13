# 当前笔记图片清单：页面数据与 DOM 双重核对

只处理用户链接指向的笔记。开始采集前已有用户指定的目录，不能因需要保存清单而默认使用项目临时目录。

## 获取与核对

1. 由 Neo 当前 URL/页面笔记链接识别目标 `noteId`，与用户打开的文章核对。使用当前 DOM 中已确认的笔记容器，不能扫描整页推荐流。
2. 在页面上下文读取 `window.__INITIAL_STATE__` 的**目标笔记条目**：桌面通常是 `note.noteDetailMap[noteId].note`，其他页面可能是 `noteData.data.noteData`。后者必须自己携带匹配的笔记 ID；前者若对象没有 ID，可用精确命中的 map key 核对。显式 ID 不匹配时停止使用该对象，重新定位；不得退而取 map 的最后一项。
3. 不导出整个初始状态，只在页面内部抽取目标 ID、图片数组及每项已有的 `urlDefault`、`url`、`infoList[].url`。优先可用的 `urlDefault`，逐项回退到 `url` 或页面明确给出的候选地址；一张缺少首选链接不能使其他图片的回退失效。默认只处理静态图片地址；若页面同时标示 Live Photo 等动态属性，在本地清单记录动态内容按范围跳过即可，不提取流地址或等待播放。清单 helper 只负责静态图片，不要求为发现动态信息另建采集链路。
4. 同时读取当前笔记的非克隆轮播页，每页只取对应主图的 `currentSrc` 和 `src`，以页序保持一一对应。记录可见计数（如 1/15 中的 15）；先确认数字含义，不从点赞数推测。
5. 使用 [scripts/xhs_image_inventory.js](../scripts/xhs_image_inventory.js) 中的 `buildXhsImageInventory(input)` 构建清单。它可在 Neo 页面上下文内执行，也可在 Node 中对已取得的精简数据执行。脚本只核对数据，不联网、不选择目录、不下载。

输入示例（示意值不是实际采集结果）：

```javascript
buildXhsImageInventory({
  expectedNoteId: '当前笔记ID',
  stateKey: '精确命中的map键；移动页不提供此值',
  stateNote: {
    noteId: '当前笔记ID',
    imageList: [{urlDefault: 'https://页面实际地址/图片', url: '', infoList: []}]
  },
  domImages: [{currentSrc: 'https://页面实际地址/图片', src: ''}],
  displayedCount: 1
});
```

在 Neo 中运行时，读取本 skill 的本地脚本源码，将 helper 声明及上述调用放入同一个 evaluate 表达式。网页值作为数据参数传递，不将网页文字拼成可执行代码。不要把 `unsafeWindow` 照搬进 Neo；它是用户脚本管理器的变量，这里使用页面上下文中的 `window`。

## 结果处理

- 每项保留 1-based `index`、`url`、`alternatives`、`domUrl`、来源和 pending 状态。缺失链接保留空槽位，不能先过滤空项导致页码前移；同图重复两次仍是两页。
- `errors` 非空或 `readyForDownload` 为 false：先处理笔记身份不符、清单为空、缺失链接或数量差异。不批量下载后再声称清单完整。
- `warnings` 提示数据缺失、无可见总数或地址差异。数据缺失时可使用 DOM，但需用可见总数/实际翻页核对并记录较低的覆盖证据。不能把 DOM 长度与自身比较当第二重证据。
- 数据与 DOM 数量不同，先观察轮播是否尚未加载、容器选错或含克隆，必要时翻页后重取。无法解释时报告缺口，不取两者较小值、截断或重新编号。
- URL 不同可能只是不同清晰度或签名，不可仅据此断言串图，也不可忽略它。检查相同页号对应的照片，必要时逐页查看；数量相同不证明内容和次序相同。
- 若 state 与 DOM 地址只在 HTTP/HTTPS 协议上不同，逐项核对主机、路径、查询与片段完全一致后，可选用 DOM 已实际提供的 HTTPS 地址，保留原值及选择理由。不能直接把任意 HTTP 字符串改成 HTTPS；其他差异仍按上一条核查。
- 只保留页面实际提供的有效地址。候选地址刷新后须再次核对笔记 ID 与页号。不剥离签名、不拼接 CDN 域名，不把特定转换参数当“原图保证”。
- `readyForDownload` 仅表示清单没有检测到硬错误；不表示文件已下载、视觉已阅读、全部警告已解决或文章已完整。

后续下载、重试、验证和读图按 [image-vision.md](image-vision.md) 执行。全部材料和失败原因留在用户采集目录，最终 Markdown 不出现技术清单。

## 借鉴来源与验证范围

参考 XHS-Downloader 在 [3261312 版本的页面数据提取](https://github.com/JoeanAmier/XHS-Downloader/blob/3261312721f0b37c705ba6515885bc7f34349f2f/static/XHS-Downloader.js#L724-L737) 和 [图片预览/下载地址映射](https://github.com/JoeanAmier/XHS-Downloader/blob/3261312721f0b37c705ba6515885bc7f34349f2f/static/XHS-Downloader.js#L620-L667) 的思路；本 helper 独立实现，没有复制上游代码。没有采用其“最后一个笔记”回退、CDN 重写或程序根目录 Temp。

合成测试覆盖笔记身份、地址回退、缺图、计数不符和重复页场景。2026-10-13 在线复测另确认了当前目标笔记 ID、state 15 项、DOM 15 项与界面总数 15 一致；逐项核对 HTTP/HTTPS 差异后采用 DOM 已提供的地址。页面字段与选择器仍需每次按 Neo 当前实际页面验证；这次成功不代表所有页面或失败路径均已验证。
