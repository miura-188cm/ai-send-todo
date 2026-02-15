# CodexでSlack MCPを動かすための実践メモ

## 1. 背景とゴール
- Slack上でチャンネル一覧の取得や日報投稿をMCP経由で自動化したい。
- 実験は Codex CLI (2026-02-14〜15) を使い、`slack-mcp-server@latest` を `npx` で都度起動する構成で実施。
- 途中で「ネットワーク遮断」「ツール登録条件」「チャンネル参加状態」など複数の落とし穴に遭遇したため、再現手順と対策を整理しておく。

## 2. サンドボックスとネットワーク制限
| 状態 | 症状 | 対処 |
| --- | --- | --- |
| `--sandbox workspace-write` などネット遮断モード | `npx slack-mcp-server` がnpmからパッケージ取得できずプロセス即死 → Codex側では `Transport closed` | Codexを `--sandbox danger-full-access` で起動し直す。ネットを許可できない場合は別ターミナルで MCP サーバーを立ち上げる。 |
| ネット許可済みでも Codex MCP ツールが即終了 | `channels_list` がユーザー/チャンネルキャッシュ生成前に叩かれプロセス終了 | サーバーを手動で起動してキャッシュ完了 (ログ: `Caching users collection...`) を待つ。必要なら独自スクリプトで `tools/call` を直接送信。 |

ポイント: Codexが内部で起動する MCP サーバーもローカル subprocess なので、**クライアントにネットが無ければサーバーもネットに出られない**。Claude 等、別クライアントで成功しても Codex では同じ制約を受ける。

## 3. slack-mcp-server の設定
`~/.codex/config.toml` に以下を追加すると、Codex 内から `codex mcp add slack ...` を使わず直接設定できる。
```toml
[mcp_servers.slack]
command = "npx"
args = ["-y", "slack-mcp-server@latest", "--transport", "stdio"]

[mcp_servers.slack.env]
SLACK_MCP_XOXB_TOKEN = "xoxb-..."              # Bot token (招待済みチャンネルのみアクセス)
SLACK_MCP_ADD_MESSAGE_TOOL = "C0AELK29807"     # 投稿を許可するチャンネルIDのホワイトリスト
SLACK_MCP_ENABLED_TOOLS = "conversations_add_message"
```
補足:
- `SLACK_MCP_ADD_MESSAGE_TOOL` を `true` にすると全チャンネル投稿可。今回は日報チャンネル限定のためIDを指定した。
- `SLACK_MCP_ENABLED_TOOLS` に `conversations_add_message` を入れないと write ツールが登録されない。
- `channels_list` や `conversations_history` のみでよければ `SLACK_MCP_ENABLED_TOOLS` は不要。

## 4. MCPツール呼び出しの検証ログ
### 4.1 channels_list
1. `scripts/channel_list_mcp.py` を作成し、`initialize` → `tools/call` を直接送信。
2. キャッシュ未完了時は `users cache is not ready yet, sync process is still running...` が返るため 2 秒リトライを数回行う。
3. 成功すると `conversations.list` と同等の JSON が返り、全チャンネルID を把握できた。

### 4.2 conversations_add_message
| 課題 | 原因 | 解決策 |
| --- | --- | --- |
| `text must be a string` | サーバー側のバグで `text` 引数を正しく解釈できないケースがある | `payload` にフォールバック (`{"channel_id":"C0...","payload":"テスト"}`) で回避。 |
| `not_in_channel` | Botユーザーがチャンネルに未参加 | Slack側で `/invite @slack_mcp_reader` を実行。 |
| 送信後にレスポンス `null` | `payload` 送信後に Slack API 側で `Missing text for attachments` 警告が出る場合がある | 投稿ログ自体は Slack に残るので、実際の可否は Slack クライアントで確認。安定性が必要なら `text` と `content_type` を併記できるパッチを upstream に投げる。 |

## 5. 直接API (curl) との比較
| 手段 | メリット | デメリット / 注意 |
| --- | --- | --- |
| MCP (`slack-mcp-server`) | Codex/Claude から統一インターフェースで呼べる。チャンネル検索や履歴取得をツールとして再利用可。 | 起動コストが高い (毎回 `npx` + キャッシュ)。write ツールは環境変数やチャンネル参加など条件が多い。サーバー実装のバグに左右される。 |
| Slack Web API 直叩き (`curl conversations.list` / `chat.postMessage`) | 単純で確実。リトライ制御しやすい。 | トークン管理とレート制限処理を自前で用意する必要がある。Codex セッションの sandbox から直接叩く場合もネット許可が必須。 |

判断基準:
- Codex/Claude から「毎回同じツールを呼ぶだけ」であれば MCP の価値は高い。
- 一度きりの情報取得や、確実性が欲しい処理は API を直接叩くほうが早い。
- 今回のようにサーバー実装の制約が多い場合は、**API をフォールバック手段として常に用意**しておくと安全。

## 6. ネックと解決策まとめ
1. **ネットワーク遮断** → Codex を `danger-full-access` で起動。無理なら別プロセスで MCP を立ててから接続。
2. **キャッシュ未生成** → MCP サーバーを起動したまま数秒待つ／独自スクリプトでリトライ。
3. **write ツール未登録** → `SLACK_MCP_ADD_MESSAGE_TOOL` と `SLACK_MCP_ENABLED_TOOLS` を設定。
4. **Ch未参加で投稿失敗** → Bot を対象チャンネルに招待。
5. **`text must be a string` エラー** → `payload` を使うか upstream fix を待つ。pull request も選択肢。

## 7. これからの運用指針
- MCP を常用するなら、`slack-mcp-server` をローカルにインストールして `npx` キャッシュを減らす。
- `send-slack` skill では投稿前にプレビュー＋承認フローを固定化しておくと事故を防げる。
- API 直叩きを fallback に組み込んだスクリプトを `scripts/` に置き、トークンの扱いを統一する。
- バグ報告 (例: `text must be a string`) は upstream issue に残し、再現条件を共有する。

以上。
