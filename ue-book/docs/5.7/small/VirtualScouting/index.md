# Virtual Scouting

> Virtual Scouting lets filmmakers scout a digital environment in virtual reality.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | VirtualScoutingOpenXR (Runtime), VirtualScouting (Runtime), VirtualScoutingEditor (Editor) |
| 创建时间 | 2022-04-21 |
| 年龄标签 | 🆕 (约 4 年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualScouting) | |

## 用途

Virtual Scouting 是一个面向影视制作的 VR 勘景工具集。它让导演、美术指导和摄影指导能够戴上 VR 头显，以第一人称视角在数字场景中"行走"，实时评估场景规模、光照、镜头构图和空间关系。

与普通的 VR Preview 不同，Virtual Scouting 提供了一整套针对影视勘景场景优化的工具：
- **视点取景器**：模拟真实摄影机的光圈、曝光和画幅比例
- **测量工具**：在 VR 中直接测量场景中的距离
- **书签系统**：标记并快速回到感兴趣的位置
- **灯光工具**：在 VR 中放置和调整灯光（Gaffer、环境光）
- **Sequencer 集成**：在 VR 中查看和编辑过场动画序列
- **抓取/变换**：在 VR 中直接抓取和移动场景物件

该 plugin 基于 OpenXR 构建，支持 Meta (Oculus) 和 SteamVR (HTC/Valve) 设备。

## 使用场景

- 你在做一个虚拟制片项目，需要让导演在 VR 中预览场景 → 启用 Virtual Scouting
- 你需要在 VR 中快速评估摄影机位置和镜头参数 → 使用 Viewfinder 工具
- 你需要在场景中标记多个勘景点，方便后续团队讨论 → 使用 Bookmark 工具
- 你需要在 VR 中测量布景尺寸是否符合设计 → 使用 Measure 工具

## 蓝图用法

### 设置类

`UVirtualScoutingSettings` 和 `UVirtualScoutingEditorSettings` 提供了通过蓝图可读写的配置项。

#### 项目级设置 (UVirtualScoutingSettings)

| 属性 | 说明 | 默认值 |
|---|---|---|
| `bUseImperial` | 测量单位是否使用英制 | `false` |
| `bViewfinderUseExposure` | 取景器是否使用自动曝光 | `false` |
| `bSwapToGrabToolOnSpawnNewActor` | 生成新 Actor 后是否自动切换到抓取工具 | `true` |
| `ViewfinderExposureCompensation` | 取景器曝光补偿 (-15 ~ 15) | `1.0` |
| `ViewfinderApertureArray` | 取景器可用光圈值列表 | `{1.2, 2.0, 2.8, 4.0, 5.6, 8.0, 11.0, 16.0, 22.0}` |
| `ViewfinderMaskArray` | 取景器画幅比例遮罩列表 | `{1.33, 1.66, 1.78, 2.0, 2.35, 2.39}` |
| `SequenceToolCollection` | Sequencer 工具使用的输入映射集合 | 空 |
| `PlacementToolCollection` | 放置工具使用的输入映射集合 | 空 |

#### 用户级设置 (UVirtualScoutingEditorSettings)

| 属性 | 说明 | 默认值 |
|---|---|---|
| `FlightSpeed` | 飞行速度 (1.0 ~ 10.0) | `4.0` |
| `DragSpeed` | 拖拽移动速度 (0.1 ~ 2.0) | `0.7` |
| `bEnableTooltips` | VR 中是否显示工具提示（手柄靠近头显时） | `true` |
| `bUseSmoothRotation` | 平滑旋转 vs 快速旋转 | `false`（快速旋转） |
| `bUseTeleportRotation` | 是否使用手柄前轴滚轮定义传送旋转方向 | `false` |

### 获取设置的蓝图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Virtual Scouting Settings` | 获取项目级 Virtual Scouting 设置 | `UVirtualScoutingSettings` |
| `Get Virtual Scouting Editor Settings` | 获取用户级编辑器设置 | `UVirtualScoutingEditorSettings` |

## C++ 用法

### 头文件引入

```cpp
#include "VirtualScoutingSettings.h"
```

### 基本用法

```cpp
// 获取项目级设置
UVirtualScoutingSettings* Settings = UVirtualScoutingSettings::GetVirtualScoutingSettings();

// 读取测量单位
bool bImperial = Settings->bUseImperial;

// 获取取景器光圈列表
const TArray<float>& Apertures = Settings->ViewfinderApertureArray;

// 获取用户级编辑器设置
UVirtualScoutingEditorSettings* EditorSettings = UVirtualScoutingEditorSettings::GetVirtualScoutingEditorSettings();
float Speed = EditorSettings->FlightSpeed;
```

### OpenXR 扩展

VirtualScoutingOpenXR 模块实现了 `IOpenXRExtensionPlugin` 接口，用于：
- 检测 VR 设备类型（Oculus vs SteamVR）
- 注册 OpenXR 可选扩展（如 `XR_EXT_debug_utils`）
- 监听 VR 编辑模式的进入/退出

```cpp
#include "VirtualScoutingOpenXRModule.h"
#include "VirtualScoutingOpenXR.h"

// 获取 OpenXR 扩展实例
FVirtualScoutingOpenXRModule& Module = FVirtualScoutingOpenXRModule::Get();
const TSharedPtr<FVirtualScoutingOpenXRExtension>& Ext = Module.GetOpenXRExt();

// 获取 HMD 设备类型的 Future
TFuture<FName>& DeviceTypeFuture = Ext->GetHmdDeviceTypeFuture();
```

### 调试日志

开启 OpenXR 调试日志：

```
// 在控制台中设置
VirtualScouting.OpenXRDebugLogging 1
```

## 内容资源

Plugin 包含丰富的蓝图资产，按功能组织在 `Content/` 目录下：

| 目录 | 说明 |
|---|---|
| `Content/Core/` | 核心框架：移动组件 (`BP_XRC_MovementComponent`)、Gizmo、默认 Scouting 模式 |
| `Content/Core/Gizmo/` | VR 变换 Gizmo 的网格和材质（平移箭头、旋转手柄、缩放手柄） |
| `Content/Core/Movement/` | XR 移动组件 |
| `Content/Tools/Bookmark/` | 书签工具：在 VR 中标记位置 |
| `Content/Tools/Viewfinder/` | 取景器工具：模拟摄影机参数 |
| `Content/Tools/Measure/` | 测量工具：在 VR 中测量距离 |
| `Content/Tools/Lighting/` | 灯光工具：环境光调色板、Gaffer 灯具 |
| `Content/Tools/Sequencer/` | Sequencer 工具：在 VR 中查看序列 |
| `Content/Input/` | 增强输入 Action 定义 |
| `Content/UI/` | UI 组件：图标、字体、材质、调试 Widget |
| `Content/Art/` | 美术资源：控制器模型、材质、后处理效果 |

## 模块依赖

### VirtualScouting (Runtime)

| 模块 | 用途 |
|---|---|
| `CommonUI` | 通用 UI 框架 |
| `Core` | UE 核心模块 |
| `XRCreative` | XR 创意工具框架（底层 VR 交互基础） |

### VirtualScoutingEditor (Editor)

| 模块 | 用途 |
|---|---|
| `OpenXRHMD` | OpenXR 头显支持 |
| `OpenXRInput` | OpenXR 输入支持 |
| `VirtualScoutingOpenXR` | 本 plugin 的 OpenXR 扩展模块 |
| `VirtualScouting` | 本 plugin 的运行时模块 |
| `VREditor` | UE 内置 VR 编辑器框架 |
| `EnhancedInput` | 增强输入系统 |
| `InteractiveToolsFramework` | 交互式工具框架 |
| `XRCreative` | XR 创意工具框架 |

### VirtualScoutingOpenXR (Runtime)

| 模块 | 用途 |
|---|---|
| `OpenXRHMD` | OpenXR 头显支持 |
| `Core` / `CoreUObject` / `Engine` / `InputCore` | 基础 UE 模块 |

### Plugin 级依赖

| Plugin | 用途 |
|---|---|
| `XRCreativeFramework` | XR 创意工具基础框架 |
| `OpenXR` | OpenXR 运行时支持 |
| `EnhancedInput` | 增强输入系统 |
| `CommonUI` | 通用 UI 框架 |
| `MultiUserClient` | 多人协作编辑支持 |
| `LiveLink` | Live Link 实时数据 |
| `GeometryScripting` | 几何脚本 |
| `GizmoFramework` | Gizmo 框架 |
| `GizmoEdMode` | Gizmo 编辑模式 |
| `ModelingToolsEditorMode` | 建模工具编辑模式 |
| `LevelSnapshots` | 关卡快照 |
| `CineCameraSceneCapture` | 电影摄影机场景捕获 |
| `VirtualProductionUtilities` | 虚拟制片工具集 |
| `ConsoleVariables` | 控制台变量管理 |
| `BlueprintFileUtils` | 蓝图文件操作 |
| `JsonBlueprintUtilities` | JSON 蓝图工具 |

## 维护状态

### ⚠️ 重要提示：已废弃

**最新 commit (2025-09-10) 将 VR Editor 模式及大部分关联类标记为废弃 (Deprecated)。** 这意味着 Virtual Scouting 的核心 VR 编辑功能已被 Epic 标记为遗留代码，未来版本可能会被移除。

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-09-10 | `cb5faa0` | VR Editor: Deprecate VR Editor mode and most associated classes | **关键变更**：VR 编辑模式被废弃，Virtual Scouting 作为 VR 编辑模式的子系统受到影响 |
| 2024-11-12 | `fa14dbd` | [Legacy Virtual Scouting] | 将 Virtual Scouting 标记为遗留系统 |
| 2024-09-25 | `086ea21` | Virtual Scouting | Virtual Scouting 从 Experimental 迁移到 VirtualProduction 目录 |

### 维护评价

- **创建时间**：2022-04-21（约 4 年前）
- **最近更新**：2025-09-10
- **维护状态**：🚫 **已废弃 (Deprecated)**
- **推荐使用**：⚠️ **不推荐用于新项目**

该 plugin 经历了从 Experimental → VirtualProduction → Deprecated 的生命周期。2024 年 9 月迁移到正式目录后，仅两个月就被标记为 Legacy，随后在 2025 年 9 月正式废弃。

如果你的项目需要 VR 勘景功能，建议：
1. 检查 UE 5.6+ 是否有替代方案（如更新的 XR Creative 工具）
2. 如果必须使用，需做好未来版本迁移的准备
3. 注意该 plugin 仅支持 Win64 平台

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualScouting)
- [XRCreativeFramework](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/XRCreativeFramework)（底层框架）
