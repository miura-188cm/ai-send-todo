---
name: send-slack
description: Slack MCPを使って、作成済みの報告文を固定チームチャンネルへ送信する。create-report/create-hokoku/create-nippo の出力を送る最終ステップで使う。
---

# send-slack

Slack MCPで報告文を送信する。送信前に必ずプレビューし、明示承認がある場合のみ投稿する。

## 入力

- `channel`: 固定チームチャンネル（MVPでは固定）
- `body`: 送信本文（Markdown可）
- `preview`: 既定値 `true`

## 手順

1. `body` が空でないことを検証する。
2. プレビュー本文を表示する。
3. ユーザーから `send` または `yes` を受け取るまで送信しない。
4. Slack MCPでチャンネルに投稿する。
5. 投稿結果として `channel` `timestamp` `permalink` を返す（取得可能な場合）。

## エラー時

- Slack MCP呼び出しに失敗した場合、要点エラーを返す。
- 失敗した本文は再送できるように保持したままにする。

## 注意点

- 承認なし送信をしない。
- 送信先を自動推定しない。
- 本文を勝手に書き換えない。
