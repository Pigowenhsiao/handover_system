; AutoIt full UI test for handover system
#include <Date.au3>
#include <Misc.au3>

Opt("WinTitleMatchMode", 4)
Opt("WinDetectHiddenText", 1)
Opt("MouseCoordMode", 2)
Opt("SendKeyDelay", 10)
Opt("SendKeyDownDelay", 10)

Global $ROOT_DIR = ""
Global $LOG_PATH = ""
Global $LOG_FILE = -1
Global $APP_PID = 0
Global $ERROR_COUNT = 0
Global $ESC_CHECK_MS = 500
Global $MAIN_TITLE = ""
Global $MAIN_HWND = 0
Global $IGNORE_TITLES = "TtkMonitorWindow"

Func InitPaths()
    Local $pos = StringInStr(@ScriptDir, "\tests", 0, -1)
    If $pos > 0 Then
        $ROOT_DIR = StringLeft(@ScriptDir, $pos - 1)
    Else
        $ROOT_DIR = @ScriptDir
    EndIf
    $LOG_PATH = $ROOT_DIR & "\tests\autoit_test_log_" & @YEAR & @MON & @MDAY & "_" & @HOUR & @MIN & @SEC & ".txt"
EndFunc

Func WriteLog($msg)
    If $LOG_FILE = -1 Then Return
    FileWriteLine($LOG_FILE, _NowCalc() & " | " & $msg)
EndFunc

Func AbortIfEsc()
    Local $timer = TimerInit()
    While TimerDiff($timer) < $ESC_CHECK_MS
        If _IsPressed("1B") Then
            WriteLog("ABORT: ESC pressed")
            If $LOG_FILE <> -1 Then FileClose($LOG_FILE)
            Exit 1
        EndIf
        Sleep(50)
    WEnd
EndFunc

Func SafeSend($keys)
    AbortIfEsc()
    Send($keys)
EndFunc

Func CloseDialogs($context, $allow)
    Local $list = WinList("[CLASS:#32770]")
    Local $count = 0
    For $i = 1 To $list[0][0]
        AbortIfEsc()
        Local $hWnd = $list[$i][1]
        If $APP_PID <> 0 Then
            If WinGetProcess($hWnd) <> $APP_PID Then ContinueLoop
        EndIf
        $count += 1
        Local $title = WinGetTitle($hWnd)
        Local $text = ControlGetText($hWnd, "", "Static1")
        If $allow Then
            WriteLog("INFO dialog: " & $title & " | " & $text & " [" & $context & "]")
        Else
            WriteLog("ERROR dialog: " & $title & " | " & $text & " [" & $context & "]")
            $ERROR_COUNT += 1
        EndIf
        WinActivate($hWnd)
        Sleep(200)
        If $allow Then
            SafeSend("{ESC}")
        Else
            SafeSend("{ENTER}")
        EndIf
        Sleep(300)
    Next
    Return $count
EndFunc

Func ExpectNoDialogs($context)
    Local $count = CloseDialogs($context, False)
    Return $count = 0
EndFunc

Func AllowDialogs($context)
    Return CloseDialogs($context, True)
EndFunc

Func GetWinPos()
    Return WinGetPos($MAIN_HWND)
EndFunc

Func ClickAt($x, $y)
    AbortIfEsc()
    MouseClick("left", $x, $y, 1, 0)
    Sleep(300)
EndFunc

Func ClickRel($xRatio, $yRatio)
    Local $pos = GetWinPos()
    If @error Then Return
    Local $x = $pos[0] + Int($pos[2] * $xRatio)
    Local $y = $pos[1] + Int($pos[3] * $yRatio)
    ClickAt($x, $y)
EndFunc

Func ClickNav($index, $name)
    Local $pos = GetWinPos()
    If @error Then Return
    Local $x = $pos[0] + 110
    Local $y = $pos[1] + 140 + ($index * 34)
    WriteLog("STEP: nav -> " & $name)
    ClickAt($x, $y)
    Sleep(700)
    ExpectNoDialogs("nav:" & $name)
EndFunc

Func WaitForMainWindow($timeoutSec)
    WriteLog("WAIT: main window")
    Local $timer = TimerInit()
    While TimerDiff($timer) < ($timeoutSec * 1000)
        AbortIfEsc()
        Local $list = WinList()
        Local $candidate = 0
        Local $candidate_area = 0
        For $i = 1 To $list[0][0]
            Local $hWnd = $list[$i][1]
            Local $title = WinGetTitle($hWnd)
            If $title = "" Then ContinueLoop
            If $APP_PID <> 0 And WinGetProcess($hWnd) = $APP_PID Then
                If StringInStr($IGNORE_TITLES, $title) Then
                    ContinueLoop
                EndIf
                If StringInStr($title, "V 0.1.5") Then
                    $MAIN_HWND = $hWnd
                    $MAIN_TITLE = $title
                    WriteLog("INFO: main window title: " & $title)
                    WinActivate($hWnd)
                    Sleep(500)
                    Return True
                EndIf
                Local $pos = WinGetPos($hWnd)
                If Not @error Then
                    Local $area = $pos[2] * $pos[3]
                    If $area > $candidate_area Then
                        $candidate_area = $area
                        $candidate = $hWnd
                    EndIf
                EndIf
            EndIf
        Next
        If $candidate <> 0 Then
            $MAIN_HWND = $candidate
            $MAIN_TITLE = WinGetTitle($candidate)
            WriteLog("WARN: main window fallback: " & $MAIN_TITLE)
            WinActivate($candidate)
            Sleep(500)
            Return True
        EndIf
        Sleep(200)
    WEnd
    WriteLog("ERROR: main window not found")
    $ERROR_COUNT += 1
    Return False
EndFunc

Func LaunchApp()
    WriteLog("STEP: launch app")
    Local $cmd = "python handover_system.py"
    AbortIfEsc()
    $APP_PID = Run($cmd, $ROOT_DIR, @SW_SHOW)
    If $APP_PID = 0 Then
        WriteLog("ERROR: failed to start app")
        $ERROR_COUNT += 1
        Return False
    EndIf
    Return WaitForMainWindow(40)
EndFunc

Func DoLogin()
    WriteLog("STEP: login")
    ClickRel(0.50, 0.42)
    SafeSend("^a")
    SafeSend("admin")
    ClickRel(0.50, 0.48)
    SafeSend("^a")
    SafeSend("admin123")
    ClickRel(0.50, 0.58)
    WriteLog("PAUSE: wait 10s for login verification")
    Sleep(10000)
    If $MAIN_HWND <> 0 Then
        Local $title = WinGetTitle($MAIN_HWND)
        If StringInStr($IGNORE_TITLES, $title) Then
            WriteLog("WARN: main hwnd is monitor window, re-detecting main window")
            WaitForMainWindow(10)
        EndIf
    Else
        WaitForMainWindow(10)
    EndIf
    If $MAIN_HWND <> 0 Then
        AbortIfEsc()
        WinMove($MAIN_HWND, "", 0, 0, @DesktopWidth, @DesktopHeight)
        WinSetState($MAIN_HWND, "", @SW_MAXIMIZE)
        Sleep(600)
    EndIf
    Sleep(1200)
    If Not ExpectNoDialogs("login") Then
        WriteLog("ERROR: login dialog appeared")
    EndIf
EndFunc

Func TestLanguageToggle()
    WriteLog("STEP: language toggle")
    ClickRel(0.78, 0.06)
    SafeSend("{DOWN}{ENTER}")
    Sleep(500)
    ClickRel(0.78, 0.06)
    SafeSend("{DOWN}{ENTER}")
    Sleep(500)
    ClickRel(0.78, 0.06)
    SafeSend("{DOWN}{ENTER}")
    Sleep(500)
EndFunc

Func TestThemeToggle()
    WriteLog("STEP: theme toggle")
    ClickRel(0.86, 0.06)
    Sleep(500)
    ClickRel(0.86, 0.06)
    Sleep(500)
EndFunc

Func TestSidebarToggle()
    WriteLog("STEP: sidebar toggle")
    ClickRel(0.16, 0.02)
    Sleep(400)
    ClickRel(0.16, 0.02)
    Sleep(400)
EndFunc

Func FillDailyReport()
    WriteLog("STEP: daily report inputs")
    ClickRel(0.32, 0.27)
    SafeSend("2025-01-15")
    ClickRel(0.32, 0.33)
    SafeSend("{F4}{DOWN}{ENTER}")
    ClickRel(0.32, 0.39)
    SafeSend("{F4}{DOWN}{ENTER}")
    ClickRel(0.28, 0.45)
    Sleep(600)
    ExpectNoDialogs("save_basic_info")

    ClickRel(0.50, 0.54)
    SafeSend("Key output test")
    ClickRel(0.50, 0.66)
    SafeSend("Key issues test")
    ClickRel(0.50, 0.78)
    SafeSend("Countermeasures test")

    ClickRel(0.42, 0.93)
    Sleep(800)
    ExpectNoDialogs("save_daily_report")

    ClickRel(0.52, 0.93)
    Sleep(600)
    AllowDialogs("reset_daily_report")
EndFunc

Func TestAttendance()
    ClickNav(1, "attendance")
    WriteLog("STEP: attendance inputs")
    ClickRel(0.35, 0.75)
    SafeSend("2")
    ClickRel(0.65, 0.75)
    SafeSend("1")
    ClickRel(0.25, 0.90)
    Sleep(600)
    ExpectNoDialogs("attendance_validate")
    ClickRel(0.78, 0.90)
    Sleep(800)
    ExpectNoDialogs("attendance_save")
EndFunc

Func TestEquipment()
    ClickNav(2, "equipment")
    WriteLog("STEP: equipment inputs")
    ClickRel(0.30, 0.30)
    SafeSend("EQ-001")
    ClickRel(0.68, 0.30)
    SafeSend("08:00")
    ClickRel(0.30, 0.38)
    SafeSend("1")
    ClickRel(0.68, 0.38)
    SafeSend("0.5")
    ClickRel(0.50, 0.48)
    SafeSend("Equipment issue test")
    ClickRel(0.50, 0.58)
    SafeSend("Action test")
    ClickRel(0.80, 0.67)
    Sleep(800)
    AllowDialogs("equipment_browse")
    ClickRel(0.34, 0.74)
    Sleep(800)
    ExpectNoDialogs("equipment_add")
    ClickRel(0.48, 0.74)
    Sleep(800)
    AllowDialogs("equipment_history")
EndFunc

Func TestLot()
    ClickNav(3, "lot")
    WriteLog("STEP: lot inputs")
    ClickRel(0.30, 0.30)
    SafeSend("LOT-001")
    ClickRel(0.50, 0.40)
    SafeSend("Lot description test")
    ClickRel(0.30, 0.50)
    SafeSend("Hold")
    ClickRel(0.50, 0.60)
    SafeSend("Notes test")
    ClickRel(0.34, 0.72)
    Sleep(800)
    ExpectNoDialogs("lot_add")
    ClickRel(0.48, 0.72)
    Sleep(800)
    AllowDialogs("lot_list")
EndFunc

Func TestSummary()
    ClickNav(4, "summary")
    WriteLog("STEP: summary dashboard")
    ClickRel(0.70, 0.27)
    Sleep(800)
    ExpectNoDialogs("summary_confirm")
    ClickRel(0.86, 0.66)
    Sleep(800)
    AllowDialogs("summary_update")
EndFunc

Func TestSummaryQuery()
    ClickNav(5, "summary_query")
    WriteLog("STEP: summary query")
    ClickRel(0.70, 0.28)
    Sleep(800)
    ExpectNoDialogs("summary_query_search")
    ClickRel(0.32, 0.36)
    SafeSend("{F4}{DOWN}{ENTER}")
    ClickRel(0.68, 0.36)
    SafeSend("{F4}{DOWN}{ENTER}")
    Sleep(500)
EndFunc

Func TestAbnormalHistory()
    ClickNav(6, "abnormal_history")
    WriteLog("STEP: abnormal history")
    ClickRel(0.70, 0.28)
    Sleep(800)
    ExpectNoDialogs("abnormal_search")
    ClickRel(0.32, 0.36)
    SafeSend("{F4}{DOWN}{ENTER}")
    ClickRel(0.68, 0.36)
    SafeSend("{F4}{DOWN}{ENTER}")
    Sleep(500)
EndFunc

Func TestDelayList()
    ClickNav(7, "delay_list")
    WriteLog("STEP: delay list")
    ClickRel(0.70, 0.28)
    Sleep(800)
    ExpectNoDialogs("delay_search")
    ClickRel(0.28, 0.40)
    Sleep(800)
    AllowDialogs("delay_import")
    ClickRel(0.42, 0.40)
    Sleep(800)
    AllowDialogs("delay_upload")
    ClickRel(0.62, 0.40)
    Sleep(800)
    ExpectNoDialogs("delay_refresh")
    ClickRel(0.78, 0.40)
    Sleep(800)
    ExpectNoDialogs("delay_clear")
EndFunc

Func TestSummaryActual()
    ClickNav(8, "summary_actual")
    WriteLog("STEP: summary actual")
    ClickRel(0.70, 0.28)
    Sleep(800)
    ExpectNoDialogs("summary_actual_search")
    ClickRel(0.28, 0.40)
    Sleep(800)
    AllowDialogs("summary_actual_import")
    ClickRel(0.42, 0.40)
    Sleep(800)
    AllowDialogs("summary_actual_upload")
    ClickRel(0.62, 0.40)
    Sleep(800)
    ExpectNoDialogs("summary_actual_clear")
EndFunc

Func TestAdmin()
    ClickNav(9, "admin")
    WriteLog("STEP: admin user mgmt")
    ClickRel(0.35, 0.30)
    SafeSend("testuser")
    ClickRel(0.62, 0.30)
    SafeSend("testuser@example.com")
    ClickRel(0.35, 0.36)
    SafeSend("Test123!")
    ClickRel(0.62, 0.36)
    SafeSend("{F4}{DOWN}{ENTER}")
    ClickRel(0.36, 0.43)
    Sleep(800)
    ExpectNoDialogs("admin_create_user")
    ClickRel(0.35, 0.60)
    Sleep(500)
    ClickRel(0.46, 0.43)
    Sleep(600)
    AllowDialogs("admin_update_user")
    ClickRel(0.56, 0.43)
    Sleep(600)
    AllowDialogs("admin_delete_user")
    ClickRel(0.66, 0.43)
    Sleep(600)
    AllowDialogs("admin_reset_password")
    ClickRel(0.76, 0.43)
    Sleep(600)
    ExpectNoDialogs("admin_reset_fields")

    WriteLog("STEP: admin master data tab")
    ClickRel(0.55, 0.22)
    Sleep(800)
    ClickRel(0.30, 0.32)
    SafeSend("TestShift")
    ClickRel(0.36, 0.39)
    Sleep(600)
    ExpectNoDialogs("admin_add_shift")
    ClickRel(0.30, 0.52)
    Sleep(300)
    ClickRel(0.44, 0.39)
    Sleep(600)
    AllowDialogs("admin_update_shift")
    ClickRel(0.54, 0.39)
    Sleep(600)
    AllowDialogs("admin_delete_shift")

    ClickRel(0.70, 0.32)
    SafeSend("TestArea")
    ClickRel(0.70, 0.39)
    Sleep(600)
    ExpectNoDialogs("admin_add_area")
    ClickRel(0.70, 0.52)
    Sleep(300)
    ClickRel(0.78, 0.39)
    Sleep(600)
    AllowDialogs("admin_update_area")
    ClickRel(0.88, 0.39)
    Sleep(600)
    AllowDialogs("admin_delete_area")

    WriteLog("STEP: admin settings tab")
    ClickRel(0.75, 0.22)
    Sleep(800)
    ClickRel(0.30, 0.36)
    Sleep(400)
    ClickRel(0.52, 0.36)
    SafeSend("5")
    ClickRel(0.70, 0.36)
    Sleep(800)
    ExpectNoDialogs("admin_save_settings")
    ClickRel(0.60, 0.26)
    Sleep(800)
    AllowDialogs("admin_browse_db")
EndFunc

Func FinishAndClose()
    WriteLog("STEP: logout")
    ClickRel(0.93, 0.06)
    Sleep(800)
    AllowDialogs("logout")

    WriteLog("STEP: close app")
    If $MAIN_HWND <> 0 Then
        AbortIfEsc()
        WinClose($MAIN_HWND)
    ElseIf $MAIN_TITLE <> "" Then
        AbortIfEsc()
        WinClose($MAIN_TITLE)
    EndIf
    Sleep(800)
    AllowDialogs("close")
EndFunc

InitPaths()
$LOG_FILE = FileOpen($LOG_PATH, 2)
If $LOG_FILE = -1 Then Exit 1
WriteLog("AutoIt UI test start")
WriteLog("Root: " & $ROOT_DIR)

If Not LaunchApp() Then
    WriteLog("ERROR: aborting due to launch failure")
    FileClose($LOG_FILE)
    Exit 1
EndIf

DoLogin()
TestLanguageToggle()
TestThemeToggle()
TestSidebarToggle()
FillDailyReport()
TestAttendance()
TestEquipment()
TestLot()
TestSummary()
TestSummaryQuery()
TestAbnormalHistory()
TestDelayList()
TestSummaryActual()
TestAdmin()
FinishAndClose()

WriteLog("AutoIt UI test complete")
WriteLog("Error count: " & $ERROR_COUNT)
FileClose($LOG_FILE)



