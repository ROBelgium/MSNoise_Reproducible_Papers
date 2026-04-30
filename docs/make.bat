@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation
REM Usage:
REM   make.bat html       -- static build, notebooks as source (no execution)
REM   make.bat html-exec  -- full build with notebook execution (needs project_bundle/)
REM   make.bat clean      -- remove _build\ and auto_papers\

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path to the executable. Alternatively you can add the
	echo.Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

if "%1" == "clean" (
	rmdir /s /q %BUILDDIR% 2>NUL
	rmdir /s /q auto_papers 2>NUL
	echo.Removed %BUILDDIR%\ and auto_papers\
	goto end
)

if "%1" == "html-exec" (
	set MRP_EXECUTE_NOTEBOOKS=always
	%SPHINXBUILD% -b html %SOURCEDIR% %BUILDDIR%\html %SPHINXOPTS% %O%
	echo.Build finished with execution: %BUILDDIR%\html\index.html
	goto end
)

%SPHINXBUILD% -b %1 %SOURCEDIR% %BUILDDIR%\%1 %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
