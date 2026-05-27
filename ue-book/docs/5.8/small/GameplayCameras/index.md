# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是一套模块化、数据驱动的摄像机系统，旨在替代和扩展 Unreal 传统的 `UCameraComponent` + `UCameraShake` 架构。它提供了基于**摄像机堆栈（Camera Stack）**和**摄像机资产（Camera Asset）**的组合式摄像机控制方式，允许开发者通过数据资产（而非硬编码）来定义摄像机行为，包括混合、过渡、震动效果等。

核心设计理念：
- **模块化**：摄像机行为拆分为独立的节点（Camera Node），可自由组合
- **数据驱动**：通过蓝图资产编辑器配置摄像机行为，无需编写 C++ 代码
- **可扩展**：支持自定义摄像机节点和求值器

该插件依赖 **EnhancedInput** 插件，用于输入与摄像机控制的集成。

## 使用场景

- 你需要一个灵活的、可在编辑器中可视化配置的摄像机系统 → 用 GameplayCameras
- 你的游戏需要多种摄像机模式（第三人称、瞄准、过场）且需要平滑过渡 → 用 GameplayCameras
- 你需要自定义复杂的摄像机行为（如弹簧臂限制、碰撞检测、多重混合）但不想硬编码 → 用 GameplayCameras
- 你在做一个需要数据驱动摄像机设计的大型项目，方便设计师独立调整 → 用 GameplayCameras

## 模块总览

| 模块 | 类型 | 说明 |
|---|---|---|
| `GameplayCameras` | Runtime | 核心运行时模块，包含摄像机堆栈、节点系统、求值器、混合逻辑等核心功能 |
| `GameplayCamerasEditor` | Runtime | 编辑器支持模块，提供摄像机资产编辑器、自定义图表编辑器、属性面板等工具 |
| `GameplayCamerasUncookedOnly` | Runtime | 仅未打包时加载的模块，包含烘焙前的数据验证和转换逻辑 |

> 详细 API 请参阅各子模块文档。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 输入系统集成，用于将玩家输入映射到摄像机控制 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 模式下摄像机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 补充和更新部分追踪通道的描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 游戏摄像机模块常规更新 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 新日志宏 |

### 维护评价

GameplayCameras 自 2020 年创建以来持续活跃维护，最近一次更新在 2026 年 5 月，保持着稳定的更新频率。近期的改动以 Bug 修复和代码质量改进为主，表明该插件已进入相对成熟阶段。

⚠️ **注意**：该插件仍标记为 `IsExperimentalVersion=true`，意味着 API 可能在未来版本中发生变化。尽管已默认启用且经过多年迭代，Epic 尚未将其标记为正式稳定版本。在生产环境中使用时需关注版本升级带来的兼容性变化。

**推荐程度**：推荐使用。作为 Epic 官方维护的下一代摄像机系统，它是 UE5 摄像机方案的未来方向，且已有足够的成熟度。但需接受其"实验性"标签带来的潜在 API 变动风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [GameplayCameras 模块文档](GameplayCameras.md)
- [GameplayCamerasEditor 模块文档](GameplayCamerasEditor.md)
- [GameplayCamerasUncookedOnly 模块文档](GameplayCamerasUncookedOnly.md)