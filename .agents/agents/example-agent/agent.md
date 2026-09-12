---
name: example-agent
description: プロジェクト固有のサブエージェント雛形。名前・説明・tools を用途に合わせて書き換える（使わなければこのフォルダごと削除）。
model: flash
tools:
  - view_file
  - list_dir
  - find_by_name
  - grep_search
subagent: true
hidden: true
---

# Agent System Instructions

（この子エージェントの役割・手順・禁止事項を書く。読み取り専用なら tools に write_to_file / replace_file_content / run_command を入れない）
