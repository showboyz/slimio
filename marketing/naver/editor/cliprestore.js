// cliprestore.js <dir> : puts back what clipsave.js wrote
ObjC.import('AppKit');
function run(argv){
  var dir=argv[0], idx=$.NSString.stringWithContentsOfFileEncodingError(dir+'/index.txt',$.NSUTF8StringEncoding,null).js;
  var pb=$.NSPasteboard.generalPasteboard; pb.clearContents;
  if (!idx) return 'empty clipboard restored';
  var byItem={};
  idx.split('\n').forEach(function(l){ var p=l.split('\t'); (byItem[p[0]]=byItem[p[0]]||[]).push(p); });
  var arr=$.NSMutableArray.array;
  Object.keys(byItem).sort().forEach(function(k){
    var it=$.NSPasteboardItem.alloc.init;
    byItem[k].forEach(function(p){ it.setDataForType($.NSData.dataWithContentsOfFile(dir+'/'+p[0]+'_'+p[1]+'.bin'), p[2]); });
    arr.addObject(it);
  });
  pb.writeObjects(arr);
  return 'restored '+Object.keys(byItem).length+' items';
}
