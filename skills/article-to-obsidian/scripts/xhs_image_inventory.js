/* Browser/Node helper. Input must contain only the current note and its carousel. */
function buildXhsImageInventory(input) {
  const { expectedNoteId, stateNote, stateKey, domImages = [], displayedCount = null } = input;
  if (!expectedNoteId || !Array.isArray(domImages)) throw new Error('需要目标笔记 ID 与当前轮播图片数组');
  const errors = [], warnings = [];
  const declaredId = stateNote && (stateNote.noteId || stateNote.note_id);
  const identityMatches = !!stateNote &&
    (declaredId ? String(declaredId) === String(expectedNoteId) : String(stateKey) === String(expectedNoteId));
  if (stateNote && !identityMatches) errors.push('state-note-id-mismatch');
  const stateImages = identityMatches && Array.isArray(stateNote.imageList) && stateNote.imageList.length
    ? stateNote.imageList : null;
  const safeUrl = value => {
    if (typeof value !== 'string' || !value) return null;
    try { const url = new URL(value); return ['http:', 'https:'].includes(url.protocol) ? url.href : null; }
    catch { return null; }
  };
  const dom = domImages.map(item => {
    const urls = [...new Set([item.currentSrc, item.src].map(safeUrl).filter(Boolean))];
    return { url: urls[0] || null, alternatives: urls.slice(1) };
  });
  if (!stateImages) warnings.push('state-images-unavailable-use-dom');
  const items = (stateImages || dom).map((item, index) => {
    const urls = stateImages ? [item.urlDefault, item.url,
      ...(Array.isArray(item.infoList) ? item.infoList.map(info => info.url) : [])]
      .map(safeUrl).filter(Boolean) : [item.url, ...item.alternatives].filter(Boolean);
    const unique = [...new Set(urls)];
    if (!unique.length) errors.push(`missing-url:${index + 1}`);
    return { index: index + 1, url: unique[0] || null, alternatives: unique.slice(1),
      domUrl: dom[index]?.url || null, source: stateImages ? 'state' : 'dom',
      downloadStatus: 'pending', visuallyRead: false };
  });
  const expectedCount = Number.isInteger(displayedCount) && displayedCount > 0 ? displayedCount : null;
  if (!items.length) errors.push('empty-image-list');
  if (stateImages && stateImages.length !== dom.length) errors.push('state-dom-count-mismatch');
  if (expectedCount !== null && expectedCount !== items.length) errors.push('displayed-count-mismatch');
  if (expectedCount === null) warnings.push('displayed-count-unavailable');
  const urlDifferences = stateImages ? items.filter(item => item.domUrl &&
    ![item.url, ...item.alternatives].includes(item.domUrl)).map(item => item.index) : [];
  if (urlDifferences.length) warnings.push('state-dom-url-differences-check-variants-or-order');
  return { noteId: String(expectedNoteId), source: stateImages ? 'state' : 'dom',
    stateCount: stateImages ? stateImages.length : null, domCount: dom.length,
    displayedCount: expectedCount, urlDifferences, errors, warnings,
    readyForDownload: errors.length === 0, items };
}
if (typeof module !== 'undefined') module.exports = { buildXhsImageInventory };
