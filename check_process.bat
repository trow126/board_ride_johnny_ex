@echo off

rem set process_name=python.exe
set process_name="Notepad.exe"
set start_process=Notepad.exe

rem �v���Z�X�`�F�b�N
tasklist | find %process_name% > NUL
if %ERRORLEVEL% == 0 (
	echo  %ERRORLEVEL% �Ώۃv���Z�X�̋N�����m�F
	goto :break
) else (
	echo %date% %time% �Ώۃv���Z�X�̒�~���m�F�A�N�����܂� >> %~dp0\check_process_log.log
	start %start_process%
	echo %start_process% >> %~dp0\check_process_log.log
)

exit