// osascript -l JavaScript fileclip.js <abs-path> : put a file on the clipboard the way Finder's Copy does (a file URL),
// so Cmd+V in the editor uploads it as a picture with its own file name. img.sh's file dialog stopped taking keys after
// the orca update of 2026-11-10 (a sheet orca cannot focus), and this needs no dialog. clipsave.js/cliprestore.js
// around the posting run keep the owner's clipboard.
ObjC.import('AppKit');
function run(argv) {
  const p = argv[0];
  if (!$.NSFileManager.defaultManager.fileExistsAtPath(p)) throw new Error('no file ' + p);
  const pb = $.NSPasteboard.generalPasteboard;
  pb.clearContents;
  if (!pb.writeObjects($([$.NSURL.fileURLWithPath(p)]))) throw new Error('clipboard write failed');
  return 'ok';
}
