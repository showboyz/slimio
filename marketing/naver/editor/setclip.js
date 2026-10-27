ObjC.import('AppKit');
function run(argv){
  var html=$.NSString.stringWithContentsOfFileEncodingError(argv[0],$.NSUTF8StringEncoding,null);
  var txt=$.NSString.stringWithContentsOfFileEncodingError(argv[1],$.NSUTF8StringEncoding,null);
  var pb=$.NSPasteboard.generalPasteboard; pb.clearContents;
  pb.setStringForType(html,'public.html'); pb.setStringForType(txt,'public.utf8-plain-text');
  return 'ok';
}
