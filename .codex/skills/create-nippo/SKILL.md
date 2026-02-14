---
name: create-nippo
description: MarkdownのTODO/状況ファイルから終業時の報告文を作成する。作業サマリー、持ち越し、懸念事項をSlack送信前にまとめるときに使う。
---

# create-nippo

Slack投稿向けの `daily_end` 報告文を生成する。

## 手順

1. 最新のTODO/状況Markdownを読む。
2. 完了作業、未完了作業、懸念事項を要約する。
3. Slack向けに短いMarkdown本文を作る。
4. `/send-slack` で明示送信確認を行う。

## 出力セクション

- 今日やったこと
- 未完了で明日に回すこと
- 現在の懸念事項

## 注意点

- 自動送信しない。
- 完了事実を推測で補完しない。
