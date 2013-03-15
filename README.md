online-rsync
============

Synchronize your local svn working copy with a remote svn working copy.
The remote svn working copy is reset and patched (based on local diff) when local modifications are made.

It uses just a ssh connection to do the job. The connection persists over time, so, 
there aren't connection handshake on every sync.