# claude-send-todo

Codex/Claude の Skill を使って、タスク整理から Slack 報告までを運用するためのリポジトリです。  
MVP は「単一リポジトリ」「固定チャンネル」「送信前の明示承認」を前提にしています。

## 何ができるか

- GitHub の担当タスクを収集して TODO に反映する
- 当日の TODO を作成・更新する
- TODO から状況報告文を作成する
- Slack MCP で報告文を送信する（承認必須）

## Skill 一覧

- `.codex/skills/gh-assigned/SKILL.md`
- `.codex/skills/create-todo/SKILL.md`
- `.codex/skills/update-todo/SKILL.md`
- `.codex/skills/create-report/SKILL.md`
- `.codex/skills/create-hokoku/SKILL.md`
- `.codex/skills/create-nippo/SKILL.md`
- `.codex/skills/send-slack/SKILL.md`

## 基本フロー（使い方）

1. `gh-assigned` で担当タスクを取得
2. `create-todo` で `TODO/YYYY/MM/DD/TODO.md` を作成/初期化
3. 日中の変更を `update-todo` で反映
4. 報告時に `create-report`（または `create-hokoku` / `create-nippo`）で本文作成
5. `send-slack` でプレビュー確認し、`send` / `yes` で送信

## TODO ファイル仕様

- 保存先: `TODO/YYYY/MM/DD/TODO.md`
- 必須セクション:
  - `## 現在の状況`
  - `## 今日やること`
  - `## 保留`
  - `## 今後やること`
- タスク表記例:
  - `- [ ] #123 タイトル (P2) (in progress)`
  - `- [x] #123 タイトル (done 2026-02-14)`

## 透明性: どう実現されているか

このリポジトリは、現時点では **Skill 定義（SKILL.md）中心**で運用しています。  
つまり、下記の特徴があります。

- 自動実行スクリプトやバックグラウンドジョブは実装していない
- 各ステップはユーザーが明示的に呼び出して進める
- 送信は `send-slack` Skill の承認フローに依存する
- 「何をするか」は SKILL.md に明記され、挙動の根拠が追える

## 透明性: 現在の制約と未実装

- `gh-assigned` は現在 `gh CLI` 前提で記述されている（GitHub MCP への移行は未反映）
- Slack 送信先は MVP では固定チャンネル運用
- 優先度は自動判定せず、都度判断
- 音声入力は未実装（テキスト入力先行）

## 運用ルール

プロジェクト方針は `.codex/AGENT.md` に定義しています。

- Skill 中心で運用する
- 承認なし送信をしない
- 合意なしで大規模実装へ進まない
