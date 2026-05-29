# Live Link MasterLockit

> Live Link support for the Ambient MasterLockit metadata server（照抄）

| 属性 | 值 |
|---|---|
| 中文名 | MasterLockit 元数据链接 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `LiveLinkMasterLockit` (Runtime), `LiveLinkMasterLockitEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkMasterLockit) | |

## 用途

为 Ambient MasterLockit 元数据服务器提供 Live Link 集成。MasterLockit 是 Ambient Recording 公司的硬件时间码/元数据同步设备，常用于多机位拍摄场景中为摄影机和录音设备提供统一的时间码和元数据标注。该插件使 UE5 能够通过 Live Link 框架接收来自 MasterLockit 服务器的元数据流，从而在虚拟制片流程中实现设备元数据与引擎的实时同步。

**为何存在**：虚拟制片需要将实拍设备的状态信息（如摄影机参数、时间码、镜头数据等）实时传入引擎。MasterLockit 作为专业影视硬件生态的一部分，该插件填补了 UE Live Link 与 Ambient 硬件之间的接入空白。

## 模块一览

| 模块 | 类型 | 职责 |
|---|---|---|
| [`LiveLinkMasterLockit`](LiveLinkMasterLockit.md) | Runtime | 核心运行时模块，负责与 MasterLockit 元数据服务器通信、解析数据并通过 Live Link 发送 |
| [`LiveLinkMasterLockitEditor`](LiveLinkMasterLockitEditor.md) | Editor | 编辑器扩展模块，提供编辑器内 MasterLockit 数据源的配置界面和创建向导 |

## 使用场景

- 你使用 Ambient MasterLockit 硬件进行多机位拍摄 → 用此插件将时间码和元数据实时同步到 UE5
- 你需要在虚拟制片流水线中获取摄影机镜头元数据（焦距、光圈等）→ 通过 Live Link MasterLockit Source 接收
- 你的拍摄现场有 MasterLockit 服务器作为主时间码源 → 此插件可替代手写 UDP/网络解析代码

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架，提供数据源/主题接口 |
| `LiveLinkInterface` | Live Link 公共接口定义 |

其余均为常见基础模块（Core、CoreUObject、Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 FSharedString 双路径 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 宏 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除 FJsonObject 中的字符串重复以释放内存 |
| 2024-10-29 | `4fb04fde` | Add support for creating json objects from utf8 strings, and utf8 strings from json objects | 增加 UTF-8 字符串与 JSON 对象的互转支持 |

### 维护评价

该插件自 2021 年创建以来**持续有基础设施级别的更新**，最近的提交集中在 2026 年 3-5 月，涉及 JSON 解析重构、日志迁移和编译警告修复。但这些更新均为引擎级通用改动（FJsonObject、UE_LOG 迁移等），**未见针对 MasterLockit 功能本身的新特性或 bug 修复**。

- 仍标记为 **Beta**（`IsBetaVersion=true`）且 `Installed=false`（默认未启用）
- 创建已 5 年，功能可能处于冻结/仅维护状态
- 适用于需要 Ambient 硬件集成的虚拟制片项目，但需自行验证兼容性

⚠️ **注意**：该插件一直处于实验/Beta 状态，未正式发布。建议在生产环境中谨慎使用，并做好替代方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkMasterLockit)
- [Live Link 框架文档](https://docs.unrealengine.com/en-US/animation-out-tools/live-link-in-unreal-engine/)