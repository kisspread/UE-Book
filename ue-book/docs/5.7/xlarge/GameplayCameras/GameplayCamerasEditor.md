# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasUncookedOnly` (UncookedOnly), `GameplayCamerasEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-09 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是 Epic 为 Unreal Engine 打造的下一代**模块化、数据驱动**相机系统。它解决的核心问题是：传统 UE 相机系统中，相机逻辑与 PlayerCameraManager 紧密耦合，难以复用、难以可视化编辑、难以在不同游戏状态间灵活切换。

该插件引入了一套全新的概念体系：

- **Camera Asset**（相机资产）：顶层容器，持有 Camera Director 和多个 Camera Rig
- **Camera Rig**（相机装备）：可复用的相机行为配置，通过**节点图**（Object Tree Graph）可视化构建
- **Camera Director**（相机导演）：决定当前激活哪个 Camera Rig，支持 Single（单一固定）和 Blueprint（蓝图驱动）两种模式
- **Camera Variable**（相机变量）：运行时可读写的参数，实现数据驱动的相机行为
- **Camera Transition**（相机过渡）：定义 Camera Rig 之间的混合与切换逻辑
- **Camera Shake Asset**（相机抖动资产）：独立于传统 CameraShake 的新抖动系统

插件深度集成 **EnhancedInput**（输入映射）、**StateTree**（状态机驱动相机切换）和 **TemplateSequence**（Sequencer 模板动画），构成完整的相机管理生态。

> ⚠️ 该插件标记为实验性（IsExperimentalVersion=true），API 可能在后续版本中发生变化。

## 使用场景

- 你在开发第三人称动作游戏，需要在探索、战斗、瞄准等状态间切换不同相机行为 → 用 Camera Director + StateTree 驱动 Camera Rig 切换
- 你需要创建可复用的相机配置（跟随相机、过肩相机、瞄准相机） → 用 Camera Rig 在节点图中可视化构建
- 你需要在不同相机之间实现平滑过渡（如从跟随相机淡入到过场相机） → 用 Camera Transition 定义过渡规则
- 你需要在运行时动态调整相机参数（FOV、臂长、偏移量） → 用 Camera Variable 实现数据驱动
- 你需要创建可配置的屏幕震动效果 → 用 Camera Shake Asset
- 你需要通过蓝图精确控制相机行为 → 用 Blueprint Camera Director 模式
- 你需要将相机动画与 Sequencer 集成 → 用 TemplateSequence 集成

## 子模块概览

本插件包含 **1086 个源文件**，是 UE5 中规模最大的相机相关插件之一。

### Runtime 模块 (`GameplayCameras`)

| 子系统 | 核心类型 | 说明 |
|---|---|---|
| Core Camera | `UCameraAsset`, `UCameraRigAsset`, `UCameraNode` | 相机资产和节点的核心类型定义 |
| Camera Variables | `UCameraVariableCollection` | 数据驱动的相机参数系统 |
| Camera Transitions | `ICameraRigTransitionOwner` | 相机之间的过渡逻辑与混合 |
| Camera Shake | `UCameraShakeAsset` | 独立的相机抖动系统 |
| Camera Directors | Single / Blueprint Director | 控制当前激活哪个 Camera Rig |
| Object Interface | `UCameraObjectInterfaceParameterBase` | 相机对象接口参数，支持外部参数注入 |
| Build System | `IHasCameraBuildStatus` | 相机资产的编译/构建状态管理 |

### Editor 模块 (`GameplayCamerasEditor`)

| 子系统 | 核心类型 | 说明 |
|---|---|---|
| Object Tree Graph | `UObjectTreeGraphSchema`, `FObjectTreeConnectionDrawingPolicy` | 自定义节点图编辑器框架 |
| Asset Editors | `UCameraAssetEditor`, `UCameraRigAssetEditor`, `UCameraShakeAssetEditor` 等 | 各类相机资产的专用编辑器 |
| Graph Schemas | `UCameraNodeGraphSchema`, `UCameraRigTransitionGraphSchema` | 图编辑器的 Schema 定义 |
| Details Customizations | `FFilmbackCameraNodeDetailsCustomization`, `FCameraAssetReferenceDetailsCustomization` | 属性面板自定义 |
| Commands | `FCameraAssetEditorCommands`, `FCameraRigAssetEditorCommands` 等 | 各编辑器的命令系统 |
| Toolkits | `FBuildButtonToolkit`, `FCameraDirectorAssetEditorMode` | 编辑器工具集和编辑模式 |
| Family System | `IGameplayCamerasFamily`, `SCameraFamilyShortcutBar` | 相机资产族管理，快捷栏 |

### UncookedOnly 模块 (`GameplayCamerasUncookedOnly`)

仅在编辑器未打包状态下加载，包含蓝图编译和资产处理逻辑。

## 蓝图用法

> ⚠️ 以下 API 基于编辑器模块源码和系统架构推断。实际运行时 BlueprintCallable 函数请参考 Runtime 模块头文件。

### 核心概念

| 概念 | 说明 | 对应资产类型 |
|---|---|---|
| Camera Asset | 顶层相机资产，包含 Director 和多个 Rig | `UCameraAsset` |
| Camera Rig | 可复用的相机行为配置 | `UCameraRigAsset` |
| Camera Rig Proxy | Camera Rig 的代理引用 | `UCameraRigProxyAsset` |
| Camera Variable | 运行时可读写的相机参数 | `UCameraVariableCollection` |
| Camera Shake | 相机抖动效果 | `UCameraShakeAsset` |

### 编辑器内使用流程

1. **创建 Camera Asset**：内容浏览器右键 → Gameplay Cameras → Camera Asset
2. **选择 Camera Director 类型**：Single（固定）或 Blueprint（蓝图驱动）
3. **添加 Camera Rig**：在 Camera Asset 编辑器中创建 Camera Rig
4. **构建节点树**：在 Camera Rig 编辑器中，从工具箱拖拽 Camera Node 到图中，连接节点构建行为树
5. **配置 Filmback**：使用 Details 面板的预设组合框选择传感器尺寸（如 Super 35mm）
6. **定义过渡**：在 Transition 编辑器中配置 Camera Rig 之间的过渡规则
7. **Build**：点击工具栏 Build 按钮编译相机资产
8. **运行时激活**：通过蓝图或 C++ 激活 Camera Asset

### Camera Rig 节点图编辑

Camera Rig 使用 Object Tree Graph 框架进行可视化编辑：

- **拖拽创建**：从工具箱（Toolbox）拖拽节点类到图中创建新节点
- **连接节点**：通过引脚（Pin）连接节点，构建相机行为树
- **数组引脚操作**：右键引脚可插入/删除数组项（Insert Before/After, Remove）
- **接口参数**：通过 `UCameraObjectInterfaceParameterGraphNode` 暴露外部可配置参数
- **注释节点**：添加 Comment 节点组织和标注节点区域
- **查找功能**：使用 Find in Camera Rig / Find in Transitions 快速定位节点

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块
#include "Core/CameraAsset.h"
#include "Core/CameraRigAsset.h"
#include "Core/CameraNode.h"
#include "Core/CameraVariableCollection.h"

// Editor 模块（仅在编辑器中使用）
#include "AssetTools/CameraAssetEditor.h"
#include "AssetTools/CameraRigAssetEditor.h"
```

### 基本用法 — 操作 Camera Asset Editor

从 `CameraAssetEditor.h` 提取的编辑器操作模式：

```cpp
// 创建并初始化 Camera Asset Editor
UCameraAssetEditor* Editor = NewObject<UCameraAssetEditor>();
Editor->Initialize(MyCameraAsset);

// 获取编辑目标
UCameraAsset* CameraAsset = Editor->GetCameraAsset();

// 获取要编辑的对象