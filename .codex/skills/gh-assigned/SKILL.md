---
name: gh-assigned
description: gh CLIで自分にアサインされたGitHub Issue/PRを取得し、Markdownのタスクリストへ正規化する。現在の担当作業確認、状況報告準備、TODO同期を行うときに使う。
---

# gh-assigned

`gh` CLIでアサイン済みタスクを収集し、TODO管理に使えるMarkdownセクションを生成する。

## 手順

1. 対象リポジトリやユーザー範囲が不明な場合はユーザーに確認する。
2. 単一リポジトリを対象に、`open` の Issue/PR のみ取得する。
3. ID、タイトル、リンクを含むMarkdown箇条書きへ整形する。
4. ラベルやマイルストーンがある場合は優先度でグループ化する。
5. ユーザーが指定したMarkdownファイルの対象セクションへ反映する。

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
