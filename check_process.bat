@echo off

rem set process_name=python.exe
set process_name="Notepad.exe"
set start_process=Notepad.exe

rem プロセスチェック
tasklist | find %process_name% > NUL
if %ERRORLEVEL% == 0 (
	echo  %ERRORLEVEL% 対象プロセスの起動を確認
	goto :break
) else (
	echo %date% %time% 対象プロセスの停止を確認、起動します >> %~dp0\check_process_log.log
	start %start_process%
	echo %start_process% >> %~dp0\check_process_log.log
)

exit