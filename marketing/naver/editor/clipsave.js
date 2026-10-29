// clipsave.js <dir> : writes every type of every clipboard item to <dir>/<item>_<n>.bin plus index.txt (item<TAB>n<TAB>type)
// Creates <dir> if needed and throws (non-zero exit) if any file can't be written, so a backup that
// didn't happen can't look like one that did.
ObjC.import('AppKit');
function run(argv){
  var dir=argv[0], pb=$.NSPasteboard.generalPasteboard, items=pb.pasteboardItems, lines=[];
  $.NSFileManager.defaultManager.createDirectoryAtPathWithIntermediateDirectoriesAttributesError(dir, true, $(), null);
  for (var i=0;i<items.count;i++){
    var it=items.objectAtIndex(i), types=it.types;
    for (var j=0;j<types.count;j++){
      var t=types.objectAtIndex(j).js, d=it.dataForType(t);
      if (!d || d.isNil()) continue;
      if (!d.writeToFileAtomically(dir+'/'+i+'_'+j+'.bin', true)) throw new Error('could not write '+dir+'/'+i+'_'+j+'.bin');
      lines.push(i+'\t'+j+'\t'+t);
    }
  }
  if (!$(lines.join('\n')).writeToFileAtomicallyEncodingError(dir+'/index.txt', true, $.NSUTF8StringEncoding, null))
    throw new Error('could not write '+dir+'/index.txt');
  return items.count+' items, '+lines.length+' types';
}
