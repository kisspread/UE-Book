# Virtual Camera Core

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟相机核心 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有 (代码) |
| 模块 | `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime), `VCamBlueprintNodes` (Runtime), `VCamCore` (Runtime), `VCamCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-18 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

Virtual Camera Core 是虚拟相机（VCam）系统的**核心运行时代码库**。它解决了通过物理设备（如平板电脑）在虚拟制片环境中**实时控制和监控摄像机**的基础架构问题。该插件提供了创建、管理和控制虚拟相机 Actor、组件以及相关工具所需的核心 C++ 类和接口，是上层插件 `VirtualCamera` 蓝图资产和内容的基础依赖。其主要价值在于提供稳定、高性能的底层支持，使得用户能够将物理设备（控制端）与 Unreal Engine 中的虚拟摄像机（视图端）无缝连接。

## 使用场景

- **虚拟制片现场**：在片场使用平板设备实时预览和控制虚拟摄像机，调整构图和运动。
- **多机位监看**：为导演或摄影指导提供多个自定义虚拟相机视角的实时画面。
- **远程协作**：通过像素流（Pixel Streaming）将虚拟相机画面推送给远程设备进行监看或控制。
- **自定义相机控制设备开发**：作为开发新型物理控制设备（如特定硬件控制器）与引擎交互的底层基础。

## 模块概览

| 模块 | 类型 | 功能简介 |
|---|---|---|
| **`VCamCore`** | Runtime | 核心运行时模块，包含虚拟相机 Actor、组件和基础控制逻辑。 |
| **`VCamBlueprintNodes`** | Runtime | 提供用于在蓝图中控制虚拟相机的专用节点。 |
| **`PixelStreamingVCam`** | Runtime | 集成像素流功能，用于将虚拟相机画面推送到远程设备。 |
| **`DecoupledOutputProvider`** | Runtime | 提供解耦的输出供给器，用于管理来自不同源（如像素流）的相机画面。 |
| **`VCamCoreEditor`** | Runtime | 编辑器扩展，提供虚拟相机相关的编辑器工具和 UI。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- [VCamCore 模块文档](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore/VCamCore.md)
- [VCamBlueprintNodes 模块文档](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore/VCamBlueprintNodes.md)
- [PixelStreamingVCam 模块文档](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore/PixelStreamingVCam.md)
- [DecoupledOutputProvider 模块文档](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore/DecoupledOutputProvider.md)
- [VCamCoreEditor 模块文档](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/VirtualCameraCore/VCamCoreEditor.md)

## 模块依赖

该插件的 `PixelStreamingVCam` 模块依赖于编辑器专用模块，这是一个独特的依赖关系：

| 模块 | 用途 |
|---|---|
| `LevelEditor` | 用于集成到关卡编辑器界面中。 |
| `UnrealEd` | 用于访问编辑器核心功能和扩展。 |

其他模块的依赖主要是常见的引擎核心模块（如 Core, CoreUObject, Engine, Slate 等），无需额外列出。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `876d5541` | Fix the crash with PIE/Simulate | 修复了在 PIE 或模拟模式下运行时的崩溃问题。 |
| 2026-05-12 | `d6533f70` | Virtual Production: Fixed warning regarding EngineAssetDefinitions plugin not being included when it | 修复了因缺少 EngineAssetDefinitions 插件导致的警告信息。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 重新分类了多个虚拟制片资产，并进行了迁移。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏 UE_LOG 迁移至新的 UE_LOGF 格式。 |
| 2026-03-09 | `8afaf39f` | Move UVPFullScreenWidget into new non-experimental plugin VirtualProduction/ViewportWidgetOverlay. | 将全屏控件从本插件移至新的非实验性插件 ViewportWidgetOverlay。 |

### 维护评价

**活跃维护**。该插件创建于 2024 年初，从实验性目录迁移而来。截至 2026 年 5 月，仍有持续的更新，包括修复关键崩溃（PIE/Simulate）、清理日志系统、重组资产分类以及模块拆分（将功能移至新插件）。这些更新表明 Epic 正在积极维护和优化该插件。

**注意事项**：`.uplugin` 明确标记为 `IsBetaVersion: true`，表明其仍为**实验性**功能。虽然维护活跃，但在生产环境中使用需评估稳定性。

**推荐**：对于虚拟制片工作流，尤其是在需要自定义相机控制或集成物理设备的场景中，**推荐使用**。开发者应意识到其实验性状态，并关注后续的更新和可能的 API 变化。