~/workspace/AGENTS.mdを読む

## 現在の構成（2026-02-21）
- 学習用プロジェクト。サイト本体は `~/workspace/http-server/public/` で管理する。
- 公開用ディレクトリは `/var/www/http-server/`。
- 反映は `~/workspace/http-server/deploy.sh` から `rsync` で行う。
- Nginx は学習用サイトを `localhost:8080` で配信する想定（`default` は原則触らない）。
- 外部公開は Cloudflare Tunnel を利用し、`panda-dev.net` を `http://localhost:8080` へ中継する。
- Cloudflare設定ファイルは `~/.cloudflared/config.yml` を使用する。
- トンネル認証情報（`~/.cloudflared/*.json`, `~/.cloudflared/cert.pem`）は機密情報としてGit管理しない。
