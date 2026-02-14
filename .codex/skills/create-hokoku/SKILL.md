---
name: create-hokoku
description: MarkdownのTODO/状況ファイルから現時点の状況報告文を作成する。現在タスク、今日やること、今後の予定、進捗、ブロッカーを送信前に整理するときに使う。
---

# create-hokoku

Slack投稿向けの `current_status` 報告文を生成する。

## 手順

1. 最新のTODO/状況Markdownと直近更新を読む。
2. 現在・今日・今後の観点で箇条書きを作る。
3. 表現は具体的かつ短くする。
4. `send-slack` skill（Slack MCP）に渡して送信確認を待つ。

## 出力セクション

- 現在の状況
- 今持っているタスク
- 今日やるタスク
- 今後やるタスク
- ブロッカー

## 注意点

- 自動送信しない。
- 不確実な項目は明示する。
- TODOパスは `TODO/YYYY/MM/DD/TODO.md` を基準に読む。
