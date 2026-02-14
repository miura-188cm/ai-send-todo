---
name: gh-assigned
description: gh CLIで自分にアサインされたGitHub Issue/PRを取得し、Markdownのタスクリストへ正規化する。現在の担当作業確認、状況報告準備、TODO同期を行うときに使う。
---

# gh-assigned

`gh` CLIでアサイン済みタスクを収集し、TODO管理に使えるMarkdownセクションを生成する。

このスキルは GitHub API（`api.github.com`）へアクセスするため、Codex 実行環境のネットワーク制限によっては実行できない。ネットワークが `restricted` の場合は「外部通信を許可した実行（承認付き実行）」に切り替える。
許可を得るときはユーザーに聞いてください

## 手順

1. まず `gh auth status` でログイン済みか確認する（未ログインなら継続不可）。
2. 対象リポジトリを現在の作業ディレクトリから特定する（単一リポジトリ前提）。
   - `gh repo view --json nameWithOwner,url`
3. `open` の Issue/PR を取得する（必要に応じて「全 open」と「@me アサイン」を両方取る）。
   - 全 open Issue: `gh issue list --state open --limit 50`
   - @me アサイン open Issue: `gh issue list --assignee @me --state open --limit 50`
   - @me アサイン open PR（必要なら）: `gh pr list --assignee @me --state open --limit 50`
4. 取得結果を Markdown のチェックリストへ正規化する（番号・タイトル・URL）。
5. 追加の文脈が必要な Issue は個別に詳細取得し、本文/ラベル/担当を補足する。
   - `gh issue view <number> --json number,title,url,state,createdAt,updatedAt,assignees,labels,author,body`
6. ユーザーが指定した Markdown ファイルの対象セクションへ反映する。

## 出力形式

ユーザー指定がなければ次の形式を使う。

```md
## GitHub Assigned
- [ ] #123 Fix login timeout (`P1`) https://github.com/org/repo/issues/123
- [ ] PR #456 Add retry logic (`review waiting`) https://github.com/org/repo/pull/456
```

## 注意点

- Issue/PR番号とURLは原文のまま保持する。
- 更新が止まっているだけで完了扱いにしない。
- `gh` 実行に失敗した場合は、失敗コマンドと要点エラーを明示する。
- 取得失敗時は古い結果を自動再利用せず、報告送信を止める。
- `error connecting to api.github.com` の場合は、認証ではなくネットワーク制限の可能性が高い。承認付き実行（外部通信許可）で再実行する。
