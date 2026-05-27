# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏相机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Editor), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是 Epic 为 UE5 打造的下一代模块化、数据驱动相机系统，旨在替代 UE4 时代基于 `UCameraComponent` + `UCameraModifier` 的传统相机架构。

该插件解决的核心问题：

1. **相机逻辑可复用**：通过 Camera Rig（相机挂载）资产将特定的相机行为（如跟随、环绕、过肩等）封装为独立的、可复用的数据资产，而非散落在各个 Blueprint 中的硬编码逻辑。
2. **可视化节点编辑**：提供基于 Object Tree Graph 的节点图编辑器，开发者可以在编辑器中以可视化方式组合相机节点（Camera Nodes），构建复杂的相机行为树。
3. **平滑过渡控制**：Camera Rig Transition 系统允许定义相机行为之间的切换条件和混合方式，实现如战斗/探索/过场等不同状态之间的自然过渡。
4. **参数化驱动**：Camera Variable 系统提供数据驱动的相机参数管理，支持变量覆盖、接口参数暴露，使得相机行为可以在运行时动态调整。
5. **与 Sequencer 集成**：提供 Sequencer Track Editor 集成，允许在过场动画中直接控制相机参数。

插件依赖 EnhancedInput，表明其设计上与现代输入系统紧密集成。

## 使用场景

- **第三人称动作游戏** → 使用 Camera Rig 封装跟随、锁定目标、自由观察等相机模式，通过 Transition 在战斗/探索间切换
- **第一人称射击游戏** → 使用 Camera Rig 定义 ADS（瞄准）、Hip-fire、Sprint 等不同视角，通过 Camera Variable 控制 FOV/偏移
- **赛车/飞行游戏** → 使用 Camera Rig 定义第三人称追尾、驾驶舱、回放等视角
- **需要在 Sequencer 中精细控制相机** → 使用 GameplayCameras 的 Sequencer Track Editor 动画化相机参数
- **需要数据驱动的相机震动** → 使用 Camera Shake Asset 通过曲线编辑器定义震动波形

## 模块总览

| 模块 | 类型 | 说明 |
|---|---|---|
| `GameplayCameras` | Runtime | 核心运行时模块，包含相机资产类型、相机节点、运行时评估逻辑 |
| `GameplayCamerasEditor` | Editor | 编辑器模块，提供节点图编辑器、资产编辑器、调试工具等 |
| `GameplayCamerasUncookedOnly` | UncookedOnly | 仅在未打包编辑器中使用的功能（如资产构建、烘焙逻辑） |

## 核心资产类型

插件定义了以下核心资产类型（位于 Runtime 模块）：

| 资产类 | 说明 |
|---|---|
| `UCameraAsset` | 主相机资产，包含完整的相机配置和相机 Director |
| `UCameraRigAsset` | 相机挂载资产，封装可复用的相机行为（节点图 + 过渡图） |
| `UCameraRigProxyAsset` | 相机挂载代理资产，用于引用间接引用 |
| `UCameraShakeAsset` | 相机震动资产，数据驱动的震动效果 |
| `UCameraVariableCollection` | 相机变量集合，管理一组 `UCameraVariableAsset` |
| `UCameraVariableAsset` | 单个相机变量，支持多种数据类型 |

## 编辑器功能

### 资产编辑器

插件为每种资产类型提供了专用的编辑器：

- **Camera Asset Editor**：编辑相机资产的 Director 逻辑和接口参数
- **Camera Rig Asset Editor**：双图编辑器——节点层级图（Node Graph）+ 过渡图（Transition Graph）
- **Camera Shake Asset Editor**：编辑震动曲线和参数
- **Camera Variable Collection Editor**：管理相机变量列表

### 蓝图用法

由于提供的源码为 Editor 模块，运行时蓝图 API（如 `UGameplayCameraComponent` 等）位于 `GameplayCameras` Runtime 模块中。以下列出 Editor 模块中可扩展的关键接口：

### 核心接口

| 接口/方法 | 说明 | 所在类 |
|---|---|---|
| `CreateCameraAssetEditor()` | 创建相机资产编辑器实例 | `IGameplayCamerasEditorModule` |
| `CreateCameraRigEditor()` | 创建相机挂载资产编辑器实例 | `IGameplayCamerasEditorModule` |
| `CreateCameraShakeEditor()` | 创建相机震动资产编辑器实例 | `IGameplayCamerasEditorModule` |
| `CreateCameraVariableCollectionEditor()` | 创建变量集合编辑器实例 | `IGameplayCamerasEditorModule` |
| `CreateCameraVariablePicker()` | 创建相机变量选择器 Widget | `IGameplayCamerasEditorModule` |
| `RegisterCameraDirectorEditor()` | 注册自定义相机 Director 编辑器 | `IGameplayCamerasEditorModule` |
| `RegisterDebugCategory()` | 注册相机调试分类 | `IGameplayCamerasEditorModule` |
| `RegisterDebugCategoryPanel()` | 注册调试分类的自定义 UI 面板 | `IGameplayCamerasEditorModule` |

### 编辑器工具类

| 类 | 说明 |
|---|---|
| `FCameraRigAssetEditorToolkitBase` | 相机挂载资产编辑器工具包基类，管理 Toolbox/Details/Graph 三面板布局 |
| `FCameraRigTransitionEditorToolkitBase` | 过渡编辑器工具包基类 |
| `FAssetEditorModeManagerToolkit` | 支持多编辑模式切换的工具包基类 |
| `FAssetEditorMode` | 编辑器模式抽象基类，支持模式间布局/工具栏切换 |
| `FCurveEditorToolkit` | 曲线编辑器工具包，管理 RichCurve 的可视化编辑 |
| `FCameraObjectInterfaceParametersToolkit` | 接口参数面板工具包 |

### 图编辑器框架

| 类 | 说明 |
|---|---|
| `UObjectTreeGraph` | 对象树图资产 |
| `UObjectTreeGraphSchema` | 对象树图的 Schema，定义连接规则、节点创建等 |
| `UObjectTreeGraphNode` | 对象树图节点，每个节点对应一个 UObject |
| `SObjectTreeGraphEditor` | 对象树图编辑器 Widget |
| `SObjectTreeGraphToolbox` | 工具箱 Widget，列出可拖拽到图中的对象类型 |
| `SFindInObjectTreeGraph` | 在对象树图中搜索节点的面板 |

### 使用示例（蓝图描述）

由于本插件主要通过编辑器 UI 操作，典型使用流程为：

1. **创建 Camera Rig Asset**：在 Content Browser 右键 → Cameras → Camera Rig Asset
2. **打开编辑器**：双击资产打开节点图编辑器
3. **从工具箱拖拽节点**：左侧 Toolbox 面板列出所有可用的 Camera Node 类型，拖拽到图中
4. **连接节点**：通过引脚连接节点建立数据流
5. **编辑过渡**：切换到 Transition Graph 标签页，定义 Camera Rig 之间的切换条件
6. **在 Camera Asset 中引用**：创建 Camera Asset，在 Director 中指定要使用的 Camera Rig

## C++ 用法

### 头文件引入

```cpp
// Editor 模块接口
#include "IGameplayCamerasEditorModule.h"

// 对象树图框架
#include "Editors/ObjectTreeGraphSchema.h"
#include "Editors/ObjectTreeGraphConfig.h"
#include "Editors/ObjectTreeGraphNode.h"

// 编辑器工具包
#include "Toolkits/CameraRigAssetEditorToolkitBase.h"
#include "Toolkits/AssetEditorModeManagerToolkit.h"
```

### 基本用法 —— 注册自定义相机 Director 编辑器

```cpp
// 来源: Public/IGameplayCamerasEditorModule.h
// 扩展相机 Director 的编辑器 UI

#include "IGameplayCamerasEditorModule.h"

// 注册一个自定义的 Director 编辑器模式
IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();

FDelegateHandle Handle = EditorModule.RegisterCameraDirectorEditor(
    FOnCreateCameraDirectorAssetEditorMode::CreateLambda(
        [](UCameraAsset* CameraAsset) -> TSharedPtr<FCameraDirectorAssetEditorMode>
        {
            // 创建并返回自定义编辑器模式
            return MakeShared<FMyCustomDirectorEditorMode>(CameraAsset);
        }
    )
);

// 使用完毕后注销
EditorModule.UnregisterCameraDirectorEditor(Handle);
```

### 基本用法 —— 注册调试分类

```cpp
// 来源: Public/IGameplayCamerasEditorModule.h
// 在相机调试器中注册自定义调试信息分类

IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();

FCameraDebugCategoryInfo CategoryInfo;
CategoryInfo.Name = TEXT("MyDebugCategory");
CategoryInfo.DisplayText = NSLOCTEXT("MyModule", "DebugCategory", "My Category");
CategoryInfo.ToolTipText = NSLOCTEXT("MyModule", "DebugTooltip", "Shows custom debug info");
CategoryInfo.IconImage = FSlateIcon(FAppStyle::GetAppStyleSetName(), "ClassIcon.Actor");

EditorModule.RegisterDebugCategory(CategoryInfo);

// 注册自定义 UI 面板（可选）
EditorModule.RegisterDebugCategoryPanel(
    TEXT("MyDebugCategory"),
    FOnCreateDebugCategoryPanel::CreateLambda(
        [](const FString& CategoryName) -> TSharedRef<SWidget>
        {
            return SNew(STextBlock).Text(FText::FromString(TEXT("Custom Debug Panel")));
        }
    )
);
```

### 进阶用法 —— 使用 Object Tree Graph 配置自定义节点图

```cpp
// 来源: Public/Editors/ObjectTreeGraphConfig.h
// 构建一个自定义对象树图的配置

FObjectTreeGraphConfig GraphConfig;
GraphConfig.GraphName = FName("MyCameraGraph");
GraphConfig.DefaultGraphNodeTitleColor = FLinearColor(0.1f, 0.3f, 0.5f);

// 注册可连接的对象类
GraphConfig.ConnectableObjectClasses.Add(UMyCameraNode::StaticClass());
GraphConfig.ConnectableObjectClasses.Add(UMyCameraModifier::StaticClass());

// 配置特定类的节点行为
FObjectTreeGraphClassConfig NodeConfig;
NodeConfig.NodeTitleColor(FLinearColor(0.8f, 0.2f, 0.1f));
NodeConfig.NodeTitleUsesObjectName(true);
NodeConfig.CanCreateNew(true);
NodeConfig.CanDelete(true);
NodeConfig.CreateCategoryMetaData(FName("MyCategory"));

GraphConfig.ObjectClassConfigs.Add(UMyCameraNode::StaticClass(), NodeConfig);
```

### 进阶用法 —— 扩展 Asset Editor Mode

```cpp
// 来源: Public/Toolkits/AssetEditorModeManagerToolkit.h
// Public/Toolkits/AssetEditorMode.h
// 创建带多模式切换的资产编辑器

class FMyCameraAssetEditorToolkit : public FAssetEditorModeManagerToolkit
{
public:
    FMyCameraAssetEditorToolkit(UAssetEditor* InOwningAssetEditor)
        : FAssetEditorModeManagerToolkit(InOwningAssetEditor)
    {
    }

    void SetupModes()
    {
        // 添加编辑模式
        auto DirectorMode = MakeShared<FAssetEditorMode>(FName("Director"));
        AddEditorMode(DirectorMode);

        auto TransitionMode = MakeShared<FAssetEditorMode>(FName("Transitions"));
        AddEditorMode(TransitionMode);

        // 切换到 Director 模式
        SetEditorMode(FName("Director"));
    }
};
```

### 进阶用法 —— Live Edit 管理

```cpp
// 来源: Private/GameplayCamerasLiveEditManager.h
// 实时编辑管理器，在编辑器中预览时同步修改

// 获取 live edit manager（通过 toolkit）
TSharedPtr<IGameplayCamerasLiveEditManager> LiveEditManager = ...;

// 监听特定 Package 的变更
LiveEditManager->AddListener(MyPackage, MyListener);

// 监听特定 CameraNode 的属性变更
LiveEditManager->AddListener(MyCameraNode, MyNodeListener);

// 编辑器中实时预览属性修改
LiveEditManager->NotifyPostEditChangeProperty(MyCameraNode, PropertyChangedEvent);
```

## Demo 示例

### 自定义调试分类注册

```cpp
// MyCameraDebugModule.h
#pragma once

#include "Modules/ModuleManager.h"
#include "IGameplayCamerasEditorModule.h"

class FMyCameraDebugModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle DirectorEditorHandle;
};
```

```cpp
// MyCameraDebugModule.cpp
#include "MyCameraDebugModule.h"

void FMyCameraDebugModule::StartupModule()
{
    IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();

    // 注册调试分类
    UE::Cameras::FCameraDebugCategoryInfo Info;
    Info.Name = TEXT("GameAnalytics");
    Info.DisplayText = NSLOCTEXT("GameAnalytics", "Debug", "Game Analytics");
    Info.ToolTipText = NSLOCTEXT("GameAnalytics", "Tooltip", "Camera analytics data");
    EditorModule.RegisterDebugCategory(Info);

    // 注册自定义 Director 编辑器扩展
    DirectorEditorHandle = EditorModule.RegisterCameraDirectorEditor(
        FOnCreateCameraDirectorAssetEditorMode::CreateLambda(
            [](UCameraAsset* CameraAsset) -> TSharedPtr<UE::Cameras::FCameraDirectorAssetEditorMode>
            {
                // 返回自定义编辑器模式
                return nullptr;
            }
        )
    );
}

void FMyCameraDebugModule::ShutdownModule()
{
    if (IGameplayCamerasEditorModule* EditorModule = 
        FModuleManager::GetModulePtr<IGameplayCamerasEditorModule>("GameplayCamerasEditor"))
    {
        EditorModule->UnregisterDebugCategory(TEXT("GameAnalytics"));
        EditorModule->UnregisterCameraDirectorEditor(DirectorEditorHandle);
    }
}

IMPLEMENT_MODULE(FMyCameraDebugModule, MyCameraDebug);
```

## 模块依赖

由于 .uplugin 明确依赖 `EnhancedInput` 插件，且 Editor 模块包含大量自定义 UI 和图编辑器框架：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 现代输入系统集成（.uplugin 插件级依赖） |
| `ObjectTreeGraph` | 对象树图编辑器框架（自定义图编辑器系统） |
| `GameplayCameras` | Runtime 核心模块（Editor 模块依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 模式下相机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 补充和更新部分 Trace 通道的描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | GameplayCameras 相关更新（commit message 简短） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |

### 维护评价

- **创建时间**：2020 年 10 月，随 UE5 早期开发引入
- **更新频率**：活跃维护中，2026 年 4-5 月仍有功能性更新和 Bug 修复
- **实验状态**：`IsExperimentalVersion=true`，仍标记为实验性功能
- **代码规模**：729 个源文件，属于大型插件，说明功能覆盖面广且仍在积极扩展
- **近期趋势**：修复运行时 Bug（PIE 变量覆盖）、代码质量改进（编译警告、日志迁移）、Trace 支持完善

**综合评价**：该插件处于**活跃维护**状态，Epic 持续投入开发资源。尽管创建已约 6 年但仍标记为实验性，说明其 API 可能在后续版本中仍有变动。作为 UE5 的核心相机系统方案，**推荐在新项目中使用**，但需注意实验性标记意味着升级时可能遇到 breaking changes。建议密切关注每个引擎版本的迁移指南。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [Editor 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras/Source/GameplayCamerasEditor)
- [Runtime 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras/Source/GameplayCameras)