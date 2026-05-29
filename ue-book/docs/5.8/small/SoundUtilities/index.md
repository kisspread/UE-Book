# Sound Utilities

> A variety of BP functions, objects, and utilities for audio.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、示例资源） |
| 模块 | `SoundUtilities` (Runtime), `SoundUtilitiesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-03-22 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundUtilities) | |

## 用途

Sound Utilities 提供了一系列实用的音频处理工具，主要用于**音量/响度计算**和**音频数据可视化**。插件解决了以下问题：

- **音量转换**：在浮点线性值（0.0-1.0）和分贝（dB）之间进行转换
- **响度分析**：计算音源在指定距离处的音量衰减，支持考虑环境影响
- **简单音源模拟**：提供简化的音源衰减模型，用于快速原型设计
- **音频资产扩展**：为编辑器提供音频相关资产的扩展操作

插件**默认未启用**（`EnabledByDefault: false`），且标记为**实验性**（`IsBetaVersion: true`），需要手动启用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `SoundUtilities` | Runtime | 核心音频工具库，提供音量/分贝转换、距离衰减计算、简单音源模拟等运行时功能 |
| `SoundUtilitiesEditor` | Editor | 编辑器扩展模块，为音频资产（Sound Wave、Sound Cue）提供右键菜单操作 |

## 使用场景

- **音频音量控制**：需要将 UI 滑块（0.0-1.0）转换为分贝值，或反之 → 使用 `VolumeToDb` / `DbToVolume`
- **距离衰减计算**：需要预计算音源在特定距离处的音量大小 → 使用 `GetSimplePhysicalMaterial` 或距离相关函数
- **音频原型设计**：需要快速搭建音频衰减逻辑而不想配置完整 Sound Attenuation → 使用 `SimpleSound` / `SimpleSoundAttenuation`
- **音频资产批处理**：需要对多个音频资产执行编辑器操作 → 使用编辑器扩展模块

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundUtilities)
- [SoundUtilities 模块文档](SoundUtilities.md)
- [SoundUtilitiesEditor 模块文档](SoundUtilitiesEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏，优化编译 |
| 2025-06-19 | `800d7a51` | Implement feedback & additional tidbits for right-click audio actions including | 实现音频资产右键菜单的反馈改进 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar | 统一 DLL 导出声明，兼容 LyraGame 构建 |
| 2025-04-11 | `b4924cdc` | Fixing crash in simple sound | 修复 SimpleSound 的崩溃问题 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件常规维护 |

### 维护评价

**维护中（活跃）** — 该插件在 2025 年仍有持续更新，包括编译优化、bug 修复和编辑器功能改进。虽然是实验性插件且默认未启用，但作为 Epic 官方音频工具集，仍在随引擎版本迭代维护。插件规模较小（14 个源文件），API 稳定。推荐在需要音频计算辅助功能时使用。