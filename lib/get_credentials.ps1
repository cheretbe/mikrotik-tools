Set-StrictMode -Version Latest
$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function StringToBase64 {
[CmdletBinding()]
param(
  [Parameter(Mandatory=$TRUE,ValueFromPipeline=$TRUE)][string]$strToEncode
)
   return [System.Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($strToEncode))
}

function Base64ToString {
[CmdletBinding()]
param(
  [Parameter(Mandatory=$TRUE,ValueFromPipeline=$TRUE)][string]$strToDecode
)
   return [System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String($strToDecode))
}

$credentials = [PSCustomObject]@{
    username = ""
    password = ""
}

if (Test-Path env:AO_MIKROTIK_CREDENTIALS) {
  $credentials = ((Base64ToString -strToDecode $env:AO_MIKROTIK_CREDENTIALS) | ConvertFrom-Json)
}

[System.Windows.Forms.Application]::EnableVisualStyles()

$form = New-Object Windows.Forms.Form
$form.Text = "Enter credentials" 
$form.ClientSize = New-Object Drawing.Size @(300, 130)
$form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
$form.Font = 'Segoe UI,11'

$nameLabel = New-Object System.Windows.Forms.Label
$nameLabel.Text = "User name:"
$nameLabel.Location = New-Object System.Drawing.Point(15, 10)
$nameLabel.TextAlign = [System.Drawing.ContentAlignment]::MiddleRight
$nameLabel.Width = 90
$nameLabel.Height = 25
$form.Controls.Add($nameLabel)

$nameTextbox = New-Object System.Windows.Forms.TextBox
$nameTextbox.Multiline = $FALSE
$nameTextbox.Location = New-Object System.Drawing.Point(115, 10)
$nameTextbox.AutoSize = $FALSE
$nameTextbox.Width = $form.ClientSize.Width - $nameTextbox.Location.X - 20
$nameTextbox.Height = 25
$nameTextbox.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor
  [System.Windows.Forms.AnchorStyles]::Left -bor
  [System.Windows.Forms.AnchorStyles]::Right
$nameTextbox.Text = $credentials.username
$form.Controls.Add($nameTextbox)

$passwordLabel = New-Object System.Windows.Forms.Label
$passwordLabel.Text = "Password:"
$passwordLabel.Location = New-Object System.Drawing.Point(15, 45)
$passwordLabel.TextAlign = [System.Drawing.ContentAlignment]::MiddleRight
$passwordLabel.Width = 90
$form.Controls.Add($passwordLabel)

$passwordTextbox = New-Object System.Windows.Forms.TextBox
$passwordTextbox.Multiline = $FALSE
$passwordTextbox.UseSystemPasswordChar = $TRUE
$passwordTextbox.Location = New-Object System.Drawing.Point(115, 45)
$passwordTextbox.AutoSize = $FALSE
$passwordTextbox.Width = $nameTextbox.Width
$passwordTextbox.Height = 25
$passwordTextbox.Anchor = [System.Windows.Forms.AnchorStyles]::Top -bor
  [System.Windows.Forms.AnchorStyles]::Left -bor
  [System.Windows.Forms.AnchorStyles]::Right
$passwordTextbox.Text = $credentials.password
$form.Controls.Add($passwordTextbox)
if ($nameTextbox.Text -ne "") { $form.ActiveControl = $passwordTextbox }

$okButton = New-Object System.Windows.Forms.Button
$okButton.Text = "OK"
$okButton.Size = New-Object System.Drawing.Size(75, 25)
$okButton.DialogResult = [System.Windows.Forms.DialogResult]::OK
$form.AcceptButton = $okButton
$form.Controls.Add($okButton)

$cancelButton = New-Object System.Windows.Forms.Button
$cancelButton.Text = "Cancel"
$cancelButton.Size = New-Object System.Drawing.Size(75, 25)
$cancelButton.Location = New-Object System.Drawing.Point(
  ($form.ClientSize.Width - $cancelButton.Size.Width - 20),
  ($form.ClientSize.Height - $cancelButton.Size.Height - 20)
)
$cancelButton.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$cancelButton.Anchor = [System.Windows.Forms.AnchorStyles]::Bottom -bor
  [System.Windows.Forms.AnchorStyles]::Right
$form.CancelButton = $cancelButton
$form.Controls.Add($cancelButton)

$okButton.Location = New-Object System.Drawing.Point(
  ($cancelButton.Location.X - $okButton.Size.Width - 10),
  $cancelButton.Location.Y
)

$form.Topmost = $True

$result = $form.ShowDialog() 

if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
  $credentials.username = $nameTextbox.Text
  $credentials.password = $passwordTextbox.Text
  Write-Output "__OK__"
  Write-Output (StringToBase64 -strToEncode ($credentials | ConvertTo-Json))
} else {
  Write-Output "Cancelled by user"
}
