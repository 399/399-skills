const assert = require('node:assert/strict');
const {buildXhsImageInventory: build} = require('../skills/article-to-obsidian/scripts/xhs_image_inventory.js');
const url = n => `https://images.example/${n}.webp`;
const base = () => ({expectedNoteId: 'target', stateKey:'target',
  stateNote:{noteId:'target',imageList:[{urlDefault:url(1)},{urlDefault:url(2)}]},
  domImages:[{src:url(1)},{currentSrc:url(2)}],displayedCount:2});
let input=base(), result=build(input);
assert.equal(result.readyForDownload,true);
assert.deepEqual(result.items.map(x=>x.index),[1,2]);
input=base(); input.stateNote.noteId='other'; result=build(input);
assert.equal(result.readyForDownload,false);
assert(result.errors.includes('state-note-id-mismatch'));
input=base();delete input.stateNote.noteId;assert.equal(build(input).source,'state');
input=base();input.stateNote=null;result=build(input);assert.equal(result.source,'dom');assert.equal(result.readyForDownload,true);
input=base();input.stateNote.imageList[1]={url:url(2)};assert.equal(build(input).items[1].url,url(2));
input=base();input.stateNote.imageList[1]={infoList:[{url:url(2)}]};assert.equal(build(input).items[1].url,url(2));
input=base();input.stateNote.imageList[0]={};result=build(input);
assert.equal(result.items.length,2);assert.equal(result.items[1].index,2);assert(result.errors.includes('missing-url:1'));
input=base();input.domImages.pop();assert(build(input).errors.includes('state-dom-count-mismatch'));
input=base();input.displayedCount=3;assert(build(input).errors.includes('displayed-count-mismatch'));
input=base();input.stateNote.imageList[1]={url:url(1)};input.domImages[1]={src:url(1)};
assert.equal(build(input).items.length,2); // Actual repeated pages must not be deduplicated.
input=base();input.domImages[0]={src:url('variant')};assert.deepEqual(build(input).urlDifferences,[1]);
input=base();input.stateNote.imageList[0]={url:'javascript:alert(1)'};assert(build(input).errors.includes('missing-url:1'));
console.log('PASS: identity, per-image fallback, missing slots, counts, repeat pages, variants and URL schemes');
