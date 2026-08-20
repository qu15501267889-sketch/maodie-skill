# 耄耋的记忆系统

这是耄耋（🐱🐱）技能自持的长期记忆，**不依赖宿主 agent 的记忆系统**——
换到一个没有全局记忆的环境，🐱🐱依然记得🐭🐭是谁、之前聊过什么。

## 隐私

**此目录由 `.gitignore` 整目录排除，不会上传到 GitHub。**
仅以下三项例外，且都不含任何对话内容：

- `README.md`（本文件）
- `user_profile.example.md`（空白模板）
- `sessions/.gitkeep`（占位文件）

## 文件说明

| 文件 | 内容 | 维护方式 |
|------|------|---------|
| `user_profile.md` | 🐭🐭的基本信息 | 手动 + 🐱🐱补充 |
| `patterns.md` | 心理模式识别记录 | 🐱🐱自动追加，编号连续 |
| `timeline.md` | 关键事件时间线 | 🐱🐱自动追加，ISO 日期 |
| `tech_notes.md` | 工具/环境笔记 | 与心理档案分开，生命周期不同 |
| `sessions/` | 对话原始存档 `YYYY-MM-DD.md` | 🐱🐱自动写入 |

## 读写方式

一律走技能工具，**禁止裸相对路径**（会落到会话工作目录，不是技能目录）：

```
skill_view(name='maodie', file_path='assets/memory/patterns.md')
skill_manage(action='write_file', name='maodie',
             file_path='assets/memory/sessions/YYYY-MM-DD.md', file_content=...)
```
