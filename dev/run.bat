for %%a in ("%~dp0..") do set "PATH=%%~fa"
xgettext.exe -n -p ..\locales -o locale.pot  -L python -D %PATH%\handlers\users\*.py %PATH%\keyboards\inline\*.py %PATH%\keyboards\default\*.py