unit Unit1;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, Vcl.MPlayer, Vcl.OleCtrls, WMPLib_TLB;

type
  TForm1 = class(TForm)
    MediaPlayer1: TWindowsMediaPlayer;
    procedure FormCreate(Sender: TObject);
    procedure FormDblClick(Sender: TObject);
  private
    { Private declarations }
    procedure RecvMsg(var Msg : TWMCopyData); message WM_COPYDATA;
  public
    { Public declarations }
  end;

var
  Form1: TForm1;

implementation

{$R *.dfm}

procedure TForm1.RecvMsg(var Msg: TWMCopyData);
var
  p : PCopyDataStruct;
  s : String;
begin
  p := PCopyDataStruct(Msg.CopyDataStruct);
  if (p <> nil) then
  begin
    SetString(s, PAnsiChar(p^.lpData), p^.cbData);
    MediaPlayer1.controls.play;

  end else
    inherited;

  Msg.Result := 1;
end;

procedure TForm1.FormCreate(Sender: TObject);
begin
  with Form1 do
  begin
    Left    := Screen.Monitors[1].Left;
    Top     := Screen.Monitors[1].Top;
    Width   := Screen.Monitors[1].Width;
    Height  := Screen.Monitors[1].Height;
  end;
  MediaPlayer1.URL := ExtractFilePath(Application.ExeName)+'ThankYou.mp4';
  MediaPlayer1.uiMode := 'none';
  MediaPlayer1.StretchToFit := True;
  MediaPlayer1.Width := Width;
  MediaPlayer1.Height := 1500;
end;

procedure TForm1.FormDblClick(Sender: TObject);
begin
  MediaPlayer1.controls.play;
end;

end.
