;Installer - Moonstone is platform for processing of medical images (DICOM).
;Written by Igor Zanotto

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------
;General

  ;Name and file
  Name "Moonstone"
  OutFile "Moonstone.exe"

  ;Default installation folder
  InstallDir "$PROGRAMFILES\Moonstone"

  ;Get installation folder from registry if available
  InstallDirRegKey HKCU "Software\Moonstone" ""

  ;Request application privileges for Windows Vista
  RequestExecutionLevel admin

  ;Compress installer
  SetCompress auto
  SetCompressor /SOLID lzma

;--------------------------------
;Variables

  ;Var MUI_TEMP
  ;Var STARTMENU_FOLDER

;--------------------------------
;Interface Configuration

  ;Show a message box with a warning when the user wants to close the installer.
  !define MUI_ABORTWARNING

  ;Show a message box with a warning when the user wants to close the uninstaller.
  !define MUI_UNABORTWARNING

  ;The icon for the installer.
  !define MUI_ICON "static\icons\installer.ico"

  ;The icon for the uninstaller.
  ;!define MUI_UNICON "static\icons\uninstaller.ico"

  ;Display an image on the header of the page.
  !define MUI_HEADERIMAGE
  !define MUI_HEADERIMAGE_BITMAP "static\header\installer-welcome.bmp"
  !define MUI_HEADERIMAGE_UNBITMAP "static\header\installer-finish.bmp"

  ;Background color for the header, the Welcome page and the Finish page.
  !define MUI_BGCOLOR "FFFFFF"

  ;Bitmap for the Welcome page and the Finish page.
  !define MUI_WELCOMEFINISHPAGE_BITMAP "static\wizard\installer-welcome.bmp"

  ;Bitmap for the Welcome page and the Finish page.
  !define MUI_UNWELCOMEFINISHPAGE_BITMAP "static\wizard\installer-finish.bmp"

;--------------------------------
;Pages

  !insertmacro MUI_PAGE_WELCOME
  !insertmacro MUI_PAGE_LICENSE "dist\COPYING"
  !insertmacro MUI_PAGE_COMPONENTS
  !insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  !insertmacro MUI_PAGE_FINISH

  !insertmacro MUI_UNPAGE_WELCOME
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  !insertmacro MUI_UNPAGE_FINISH

;--------------------------------
;Languages

  !insertmacro MUI_LANGUAGE "English" ;first language is the default language
  !insertmacro MUI_LANGUAGE "French"
  !insertmacro MUI_LANGUAGE "German"
  !insertmacro MUI_LANGUAGE "Spanish"
  !insertmacro MUI_LANGUAGE "SimpChinese"
  !insertmacro MUI_LANGUAGE "TradChinese"
  !insertmacro MUI_LANGUAGE "Japanese"
  !insertmacro MUI_LANGUAGE "Korean"
  !insertmacro MUI_LANGUAGE "Italian"
  !insertmacro MUI_LANGUAGE "Dutch"
  !insertmacro MUI_LANGUAGE "Danish"
  !insertmacro MUI_LANGUAGE "Swedish"
  !insertmacro MUI_LANGUAGE "Norwegian"
  !insertmacro MUI_LANGUAGE "NorwegianNynorsk"
  !insertmacro MUI_LANGUAGE "Finnish"
  !insertmacro MUI_LANGUAGE "Greek"
  !insertmacro MUI_LANGUAGE "Russian"
  !insertmacro MUI_LANGUAGE "Portuguese"
  !insertmacro MUI_LANGUAGE "PortugueseBR"
  !insertmacro MUI_LANGUAGE "Polish"
  !insertmacro MUI_LANGUAGE "Ukrainian"
  !insertmacro MUI_LANGUAGE "Czech"
  !insertmacro MUI_LANGUAGE "Slovak"
  !insertmacro MUI_LANGUAGE "Croatian"
  !insertmacro MUI_LANGUAGE "Bulgarian"
  !insertmacro MUI_LANGUAGE "Hungarian"
  !insertmacro MUI_LANGUAGE "Thai"
  !insertmacro MUI_LANGUAGE "Romanian"
  !insertmacro MUI_LANGUAGE "Latvian"
  !insertmacro MUI_LANGUAGE "Macedonian"
  !insertmacro MUI_LANGUAGE "Estonian"
  !insertmacro MUI_LANGUAGE "Turkish"
  !insertmacro MUI_LANGUAGE "Lithuanian"
  !insertmacro MUI_LANGUAGE "Catalan"
  !insertmacro MUI_LANGUAGE "Slovenian"
  !insertmacro MUI_LANGUAGE "Serbian"
  !insertmacro MUI_LANGUAGE "SerbianLatin"
  !insertmacro MUI_LANGUAGE "Arabic"
  !insertmacro MUI_LANGUAGE "Farsi"
  !insertmacro MUI_LANGUAGE "Hebrew"
  !insertmacro MUI_LANGUAGE "Indonesian"
  !insertmacro MUI_LANGUAGE "Mongolian"
  !insertmacro MUI_LANGUAGE "Luxembourgish"
  !insertmacro MUI_LANGUAGE "Albanian"
  !insertmacro MUI_LANGUAGE "Breton"
  !insertmacro MUI_LANGUAGE "Belarusian"
  !insertmacro MUI_LANGUAGE "Icelandic"
  !insertmacro MUI_LANGUAGE "Malay"
  !insertmacro MUI_LANGUAGE "Bosnian"
  !insertmacro MUI_LANGUAGE "Kurdish"
  !insertmacro MUI_LANGUAGE "Irish"
  !insertmacro MUI_LANGUAGE "Uzbek"

;--------------------------------
;Reserve Files

  ;If you are using solid compression, files that are required before
  ;the actual installation should be stored first in the data block,
  ;because this will make your installer start faster.

  !insertmacro MUI_RESERVEFILE_LANGDLL

;--------------------------------
;Installer Sections

Section "Moonstone" SecApp

  SetOutPath "$INSTDIR"

  File /r "dist\*.*"

  ;Store installation folder
  WriteRegStr HKCU "Software\Moonstone" "" $INSTDIR

  ;Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  SetOutPath "$SMPROGRAMS\Moonstone\"

  ;User directory config
  IfFileExists "$PROFILE\.moonstone\" isuserconfig createuserconfig
    isuserconfig:
      MessageBox MB_YESNO "Want to write about user settings?" IDYES createuserconfig

  createuserconfig:
    CreateDirectory "$PROFILE\.moonstone\"
    CreateDirectory "$PROFILE\.moonstone\resources\"
    CopyFiles "$INSTDIR\resources\logging.conf" "$PROFILE\.moonstone\resources\"
    CreateDirectory "$PROFILE\.moonstone\resources\ilsa\"
    CopyFiles "$INSTDIR\resources\ilsa\plugin.conf" "$PROFILE\.moonstone\resources\ilsa\"
    CreateDirectory "$PROFILE\.moonstone\log\"
    SetFileAttributes "$PROFILE\.moonstone\" HIDDEN

  ;Shortcuts"
  SetOutPath "$INSTDIR"
  CreateShortCut "$INSTDIR\Moonstone.lnk" "$INSTDIR\Moonstone.exe"
  CreateShortCut "$SMPROGRAMS\Moonstone\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  CopyFiles "$INSTDIR\Moonstone.lnk" "$SMPROGRAMS\Moonstone\"
  CopyFiles "$INSTDIR\Moonstone.lnk" "$DESKTOP\"
  Delete "$INSTDIR\Moonstone.lnk"  
 
  SetOutPath "$SMPROGRAMS\Moonstone\"

  ;AccessControl::GrantOnFile "$INSTDIR" "(S-1-5-32-545)" "FullAccess"
SectionEnd

;--------------------------------
;Installer Functions

;Function .onInit

;  !insertmacro MUI_LANGDLL_DISPLAY

;FunctionEnd

;--------------------------------
;Descriptions

  ;Language strings
  LangString DESC_SecApp ${LANG_ENGLISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_PORTUGUESEBR} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_PORTUGUESE} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_FRENCH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_GERMAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_SPANISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_SIMPCHINESE} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_TRADCHINESE} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_JAPANESE} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_KOREAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_ITALIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_DUTCH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_DANISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_SWEDISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_NORWEGIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_NORWEGIANNYNORSK} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_FINNISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_GREEK} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_RUSSIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_POLISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_UKRAINIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_CZECH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_SLOVAK} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_CROATIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_BULGARIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_HUNGARIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_THAI} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_ROMANIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_LATVIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_MACEDONIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_ESTONIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_TURKISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_LITHUANIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_CATALAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_SLOVENIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_SERBIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_SERBIANLATIN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_ARABIC} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_FARSI} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_HEBREW} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_INDONESIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_MONGOLIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_LUXEMBOURGISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_ALBANIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_BRETON} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_BELARUSIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_ICELANDIC} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_MALAY} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_BOSNIAN} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_KURDISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_IRISH} "Moonstone is platform for processing of medical images (DICOM)."
  LangString DESC_SecApp ${LANG_UZBEK} "Moonstone is platform for processing of medical images (DICOM)."

  ;Assign language strings to sections
  !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SecApp} $(DESC_SecApp)
  !insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  Delete "$INSTDIR\*.*"

  Delete "$DESKTOP\Moonstone.lnk"
  Delete "$SMPROGRAMS\Moonstone\Moonstone.lnk"
  Delete "$SMPROGRAMS\Moonstone\Uninstall.lnk"

  RMDir /r "$SMPROGRAMS\Moonstone\resources"
  RMDir  "$SMPROGRAMS\Moonstone\"

  RMDir /r "$INSTDIR\resources\"
  RMDir "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\Moonstone"

SectionEnd

;--------------------------------
;Uninstaller Functions

;Function un.onInit

;  !insertmacro MUI_UNGETLANGUAGE

;FunctionEnd
