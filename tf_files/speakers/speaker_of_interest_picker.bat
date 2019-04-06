@ECHO off
for /d %%d in (*.*) do if %%d NEQ %1 if %%d NEQ %2 if %%d NEQ %3 if %%d NEQ %4 (mkdir other & move %%d\*.* other & rmdir %%d)
pause