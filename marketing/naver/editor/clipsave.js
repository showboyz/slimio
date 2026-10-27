// clipsave.js <dir> : writes every type of every clipboard item to <dir>/<item>_<n>.bin plus index.txt (item<TAB>n<TAB>type)
ObjC.import('AppKit');
function run(argv){
  var dir=argv[0], pb=$.NSPasteboard.generalPasteboard, items=pb.pasteboardItems, lines=[];
  for (var i=0;i<items.count;i++){
    var it=items.objectAtIndex(i), types=it.types;
    for (var j=0;j<types.count;j++){
      var t=types.objectAtIndex(j).js, d=it.dataForType(t);
      if (!d || d.isNil()) continue;
      d.writeToFileAtomically(dir+'/'+i+'_'+j+'.bin', true);
      lines.push(i+'\t'+j+'\t'+t);
    }
  }
  $(lines.join('\n')).writeToFileAtomicallyEncodingError(dir+'/index.txt', true, $.NSUTF8StringEncoding, null);
  return items.count+' items, '+lines.length+' types';
}
