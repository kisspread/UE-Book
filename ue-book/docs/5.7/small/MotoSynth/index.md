# MotoSynth

> An experimental granular vehicle engine. Intended to explore and demonstrate potential capabilities. Not supported.

| 属性 | 值 |
|---|---|
| 中文名 | 摩托车合成引擎 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音效预设、音频资产） |
| 模块 | `MotoSynth` (Runtime), `MotoSynthEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotoSynth) | |

## 总体用途

MotoSynth 是一个**实验性粒状合成音频引擎**，专为模拟车辆发动机（尤其是摩托车）的复杂声音而设计。它利用粒状合成技术，根据发动机转速、负载等实时参数生成动态、逼真的引擎音色。插件提供易于配置的预设资产（`UMotoSynthPreset`）和运行时音效源（`USynthSoundMotoSynth`），允许开发者无需深度音频编程即可为车辆音频增加层次感和真实感。由于声明为“非支持”（Not supported），该插件主要用于探索和原型验证。

## 模块列表

| 模块 | 类型 | 一句话总结 | 文档 |
|---|---|---|---|
| `MotoSynth` | Runtime | 核心运行时模块，提供粒状合成引擎、预设资产、音频组件以及蓝图/C++ API。 | [MotoSynth.md](./MotoSynth.md) |
| `MotoSynthEditor` | Editor | 编辑器模块，提供预设编辑工具、资产类型操作以及通知图标等 UI 辅助。 | [MotoSynthEditor.md](./MotoSynthEditor.md) |

## 使用场景

- **车辆类游戏**：摩托车、赛车、越野车等需要动态发动机声音的场景，特别是当转速、节气门开度随时变化时。
- **原型开发**：在项目早期尝试粒状合成音频效果，评估是否满足风格需求。
- **音频技术演示**：展示 UE5 粒状合成能力，为音频设计师提供灵感。

## 维护状态

### 近期更新

- 2025-08-28 `08e89bc9` — fixup `ISoundGenerator::GetNextBuffer()` implementers (don't assume zero'd buffer)
- 2025-06-19 `800d7a51` — Implement feedback & additional tidbits for right-click audio actions including
- 2025-04-23 `939cc6e5` — Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv
- 2024-11-10 `66e9bb39` — Removed all `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` scopes from the code base
- 2024-07-29 `0084b0f6` — CIS Followup - deleting pointer to incomplete type.

### 维护评价

创建于 2024 年 7 月，至今持续有功能性修复和改进（最近更新距当前约 2 个月），维护状态为**活跃**。但插件明确声明为实验性、非支持，可能存在 API 不稳定或性能未优化的情况。适合于愿意接受实验性风险的团队，不建议用于商业项目的主音频方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MotoSynth)
- [MotoSynth 运行时模块文档](./MotoSynth.md)
- [MotoSynthEditor 编辑器模块文档](./MotoSynthEditor.md)