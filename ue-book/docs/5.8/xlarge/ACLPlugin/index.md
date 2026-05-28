# ACLPlugin

> Use the Animation Compression Library (ACL) to compress AnimSequences.

| 属性 | 值 |
|---|---|
| 中文名 | 动画压缩库 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画压缩设置） |
| 模块 | `ACLPlugin` (Runtime), `ACLPluginEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ACLPlugin) | |

## 用途

ACL（Animation Compression Library）是由 Nicholas Frechette 开发的开源高性能动画压缩库，Epic 将其集成为 UE5 内置插件。它解决了 UE 默认动画压缩算法在**压缩比**和**解压速度**上的瓶颈：

- **压缩率更高**：相比 UE 默认压缩，ACL 能在相同质量下将动画数据体积减少 30%–50%，对打包体积和内存占用有显著优化。
- **解压更快**：ACL 的解压路径经过 SIMD 优化，解压速度显著快于 UE 默认方案，适合大量骨骼动画同时播放的场景。
- **质量可控**：提供精度（accuracy）和压缩比之间的灵活权衡，支持按骨骼轨道独立调整。

该插件可以作为 UE 默认动画压缩 Codec 的**直接替代品**，无需修改动画资产即可切换使用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [`ACLPlugin`](ACLPlugin.md) | Runtime | 核心压缩/解压运行时逻辑，注册 ACL 为动画压缩 Codec |
| [`ACLPluginEditor`](ACLPluginEditor.md) | Editor | 编辑器集成，提供压缩配置 UI 和动画数据控制器支持 |

## 使用场景

- 你的项目有**大量 AnimSequence 资产**，打包体积过大 → 用 ACL 替代默认压缩，显著减小包体
- 你需要在运行时**同时播放大量骨骼动画**（如百人同屏）→ ACL 的快速解压路径降低 CPU 开销
- 你对动画**质量敏感**，但又需要高压缩比 → ACL 的精度控制让你在质量和大小之间精确权衡
- 你正在做**跨平台项目**，需要一致的动画压缩表现 → ACL 作为统一 Codec 覆盖所有平台

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TraceLog` | 运行时压缩/解压性能追踪 |
| `DesktopPlatform` | 平台相关功能调用 |
| `AnimationDataController` | 编辑器中动画数据的批量处理控制 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新 API |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次批量替换错误 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退有问题的提交 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 修复委托注册遗漏，适配引擎 API 变更 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 清理过时的静态分析抑制标记 |

### 维护评价

ACLPlugin 作为 UE5 内置的动画压缩方案，处于**稳定维护**状态。最近的更新集中在引擎 API 适配（委托签名变更、日志宏迁移）和代码质量维护（静态分析清理），属于常规维护性质，无功能性 bug 修复或新特性引入，说明插件本身已相当成熟。

- ✅ 仍在跟随引擎主线同步维护
- ✅ 默认启用，Epic 官方推荐的动画压缩方案
- ✅ 无已知废弃标记
- ⚠️ 实际压缩库代码（ACL 核心）维护在外部仓库，引擎内主要是集成层

**推荐使用**：如果你的项目对动画压缩有需求，强烈建议启用 ACL 替代默认方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ACLPlugin)
- [ACL 官方仓库](https://github.com/nfrechette/acl)