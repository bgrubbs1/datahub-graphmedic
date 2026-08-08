$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$videoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$text = Get-Content -Raw -LiteralPath (Join-Path $videoRoot 'narration.txt')
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.Rate = 1
$voice.Volume = 100
$voice.SetOutputToWaveFile((Join-Path $videoRoot 'public\narration.wav'))
$voice.Speak($text)
$voice.Dispose()
