~/workspace/AGENTS.mdを読む

## 現在の構成（2026-02-22）
- 学習用プロジェクト。サイト本体は `~/workspace/http-server/public/` で管理する。
- 公開用ディレクトリは `/var/www/http-server/`。
- 反映は `~/workspace/http-server/deploy.sh` から `rsync` で行う。
- Nginx は学習用サイトを `127.0.0.1:8080` で配信する（Cloudflare Tunnel 前提のローカル限定待ち受け）。
- Nginx の `default` サイトは無効化済み（`80/tcp` の待ち受けは使わない）。
- 外部公開は Cloudflare Tunnel を利用し、`panda-dev.net` を `http://localhost:8080` へ中継する。
