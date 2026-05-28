# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机系统 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具、图表框架） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

---

## 用途

GameplayCameras 是 Epic 开发的**下一代模块化、数据驱动摄像机系统**，旨在取代 UE5 中传统的 CameraComponent/CameraShake 工作流。

核心设计理念：
- **数据驱动**：摄像机行为定义为资产（CameraAsset、CameraRigAsset），而非硬编码 C++ 类
- **节点图编辑**：通过可视化的对象树图表（ObjectTreeGraph）编排摄像机节点层级
- **参数化接口**：CameraRig 通过 Interface Parameters 暴露可覆盖的参数，实现灵活组合
- **过渡系统**：支持摄像机之间的条件过渡（Transitions），包含进入/退出条件
- **变量系统**：CameraVariable 支持在运行时动态修改摄像机参数
- **Sequencer 集成**：支持在 Sequencer 中对摄像机参数进行关键帧动画
- **实时预览**：LiveEdit 系统支持在编辑器中实时预览摄像机效果

### 与传统系统的对比

| 特性 | 传统系统 | GameplayCameras |
|---|---|---|
| 配置方式 | C++ 继承 + Blueprint | 数据资产 + 节点图 |
| 参数修改 | 硬编码属性 | 变量引用 + 属性包覆盖 |
| 组合方式 | UCameraComponent 嵌套 | CameraRig 模块化组合 |
| 过渡逻辑 | 状态机 C++ 代码 | 图表驱动条件过渡 |
| 编辑器集成 | 无专用编辑器 | 专用资产编辑器 |

---

## 模块架构

```
GameplayCameras/
├── Source/
│   ├── GameplayCameras/              ← 核心运行时模块（摄像机评估、资产类、变量系统）
│   ├── GameplayCamerasEditor/        ← 编辑器模块（资产编辑器、图表框架、Sequencer 集成）
│   └── GameplayCamerasUncookedOnly/  ← 仅未打包模块（编译工具等）
├── GameplayCameras.uplugin
└── Content/                          ← 蓝图资产和模板
```

### 核心资产类型

| 资产类型 | 说明 |
|---|---|
| `UCameraAsset` | 顶层摄像机资产，包含完整的摄像机配置 |
| `UCameraRigAsset` | 摄像机装备资产，可复用的摄像机组件 |
| `UCameraRigProxyAsset` | 摄像机装备代理资产，间接引用 |
| `UCameraShakeAsset` | 摄像机震动资产，数据驱动的震动效果 |
| `UCameraVariableCollection` | 摄像机变量集合，管理运行时可修改的参数 |
| `UCameraVariableAsset` | 单个摄像机变量（支持多种类型） |

---

## 使用场景

- 你需要一个**模块化、可复用的摄像机系统** → 使用 GameplayCameras 的 CameraRig 资产
- 你想要**可视化编辑摄像机行为**而非编写 C++ → 使用节点图编辑器
- 你需要**运行时动态切换摄像机**（如过场动画 → 游戏玩法） → 使用 CameraAsset + Transitions
- 你需要**在 Sequencer 中关键帧化摄像机参数** → 使用 Sequencer 集成
- 你需要**数据驱动的摄像机震动** → 使用 CameraShakeAsset

---

## 蓝图用法

> ⚠️ 由于本插件标记为实验性（IsExperimentalVersion=true），蓝图 API 可能发生变化。以下基于源码分析的公开接口。

### 核心运行时 API

从运行时模块的公开接口推断，核心用法围绕 `GameplayCameraComponent`：

| 功能 | 说明 | 所在类 |
|---|---|---|
| `GameplayCameraComponent` | 挂载到 Actor 上的摄像机组件，运行 CameraAsset | `UGameplayCameraComponentBase` |
| CameraAsset 配置 | 设置要使用的摄像机资产 | — |
| CameraVariable 读写 | 运行时读取/设置摄像机变量值 | `UCameraVariableAsset` |

### 蓝图使用流程（文字描述）

1. **创建 CameraVariableCollection**：在内容浏览器右键 → GameplayCameras → CameraVariableCollection
2. **创建 CameraRigAsset**：右键 → GameplayCameras → CameraRigAsset，然后在节点图编辑器中编排摄像机节点
3. **创建 CameraAsset**：右键 → GameplayCameras → CameraAsset，组合多个 CameraRig 并配置过渡条件
4. **在 Actor 中使用**：给 Actor 添加 `UGameplayCameraComponentBase`，设置 CameraAsset 属性

---

## 编辑器工具（GameplayCamerasEditor）

本插件提供了一套完整的专用编辑器框架。

### 对象树图表框架（ObjectTreeGraph）

这是 GameplayCameras 最核心的编辑器基础设施，提供了一个**通用的对象树可视化编辑系统**。

#### 核心类

| 类 | 说明 |
|---|---|
| `FObjectTreeGraphConfig` | 图表配置，定义可连接的对象类、节点外观、行为 |
| `UObjectTreeGraphSchema` | 图表 Schema，管理连接规则、上下文菜单、节点创建 |
| `UObjectTreeGraphNode` | 图表节点，表示一个 UObject 实例 |
| `SObjectTreeGraphEditor` | 图表编辑器 Slate 控件 |
| `SObjectTreeGraphToolbox` | 工具箱控件，列出可添加的节点类型 |

#### 图表配置系统

`FObjectTreeGraphConfig` 通过流式 API 配置图表行为：

```cpp
// 定义哪些类可以在图表中作为节点
Config.ConnectableObjectClasses.Add(UMyCameraNode::StaticClass());

// 为特定类配置节点外观
FObjectTreeGraphClassConfig NodeConfig;
NodeConfig.NodeTitleColor(FLinearColor::Red);
NodeConfig.NodeTitleTextColor(FLinearColor::White);
NodeConfig.HasSelfPin(true);
Config.ObjectClassConfigs.Add(UMyCameraNode::StaticClass(), NodeConfig);
```

#### 自定义 Pin 类型

图表支持三种自定义 Pin 类型：
- `PC_CameraParameter` — 摄像机参数 Pin
- `PC_CameraVariableReference` — 变量引用 Pin
- `PC_CameraContextData` — 上下文数据 Pin

### 资产编辑器体系

| 编辑器 | 说明 |
|---|---|
| `FCameraAssetEditorToolkit` | CameraAsset 的编辑器，支持多种模式（Director、SharedTransitions 等） |
| `FCameraRigAssetEditorToolkitBase` | CameraRig 的编辑器基类，提供节点图 + 过渡图双面板 |
| `FCameraShakeAssetEditorToolkit` | CameraShake 的编辑器 |
| `FCameraRigTransitionEditorToolkitBase` | 过渡逻辑编辑器基类 |
| `FCameraVariableCollectionEditorToolkit` | 变量集合编辑器 |

### 编辑器模式系统

`FAssetEditorModeManagerToolkit` 提供了类似 UE 编辑器模式（Editor Mode）的机制：

```cpp
// 添加编辑模式
AddEditorMode(MakeShared<FMyCameraAssetEditorMode>());

// 切换模式
SetEditorMode(FName("DirectorMode"));
```

### 接口参数面板

摄像头对象可以暴露可覆盖的接口参数（Interface Parameters），支持：
- 参数定义与 Getter 节点
- 属性包覆盖（Property Bag Override）
- 参数浏览器选择器

### Sequencer 集成

`FGameplayCameraComponentTrackEditor` 为 Sequencer 提供摄像机参数轨道支持：
- 自动发现 CameraComponent 上的关键帧化属性
- 支持嵌套属性路径的子菜单
- 支持拖放 CameraVariable 到 Sequencer

### 调试工具

- `SGameplayCamerasDebugger` — 摄像机系统调试器面板
- `FCameraSystemTraceModule` — UnInsights 追踪模块（`-tracegameplaycameras`）
- 可注册自定义调试类别和面板

### 实时编辑

`FGameplayCamerasLiveEditManager` 支持：
- 资产构建后实时通知监听器
- CameraNode 属性修改实时通知
- PIE 开始时自动清理

### 曲线编辑

- `FCurveEditorToolkit` — 通用曲线编辑器工具包
- `SRichCurveViewport` — RichCurve 视口控件
- 支持单值、Rotator、Vector 类型的曲线自定义

---

## C++ 用法

### 头文件引入

```cpp
// 运行时
#include "GameplayCamerasModule.h"

// 编辑器
#include "IGameplayCamerasEditorModule.h"
```

### 基本用法 — 获取编辑器模块

```cpp
// 来源: Public/IGameplayCamerasEditorModule.h
IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();
```

### 创建资产编辑器

```cpp
// 来源: Public/IGameplayCamerasEditorModule.h
// 创建 CameraAsset 编辑器
UCameraAssetEditor* Editor = EditorModule.CreateCameraAssetEditor(
    EToolkitMode::Standalone,
    TSharedPtr<IToolkitHost>(),
    MyCameraAsset
);

// 创建 CameraRig 编辑器
UCameraRigAssetEditor* RigEditor = EditorModule.CreateCameraRigEditor(
    EToolkitMode::Standalone,
    TSharedPtr<IToolkitHost>(),
    MyCameraRig
);

// 创建变量集合编辑器
UCameraVariableCollectionEditor* VarEditor = EditorModule.CreateCameraVariableCollectionEditor(
    EToolkitMode::Standalone,
    TSharedPtr<IToolkitHost>(),
    MyVariableCollection
);
```

### 注册自定义摄像机 Director 编辑器

```cpp
// 来源: Public/IGameplayCamerasEditorModule.h
// 自定义 Director 模式的编辑器模式
FOnCreateCameraDirectorAssetEditorMode CreateModeDelegate;
CreateModeDelegate.BindLambda([](UCameraAsset* CameraAsset) -> TSharedPtr<FCameraDirectorAssetEditorMode>
{
    return MakeShared<FMyCustomDirectorMode>(CameraAsset);
});

FDelegateHandle Handle = EditorModule.RegisterCameraDirectorEditor(CreateModeDelegate);

// 不再需要时注销
EditorModule.UnregisterCameraDirectorEditor(Handle);
```

### 注册调试类别

```cpp
// 来源: Public/IGameplayCamerasEditorModule.h
FCameraDebugCategoryInfo DebugCategory;
DebugCategory.Name = TEXT("MyCameraDebug");
DebugCategory.DisplayText = NSLOCTEXT("MyModule", "DebugCategory", "My Camera Debug");
DebugCategory.ToolTipText = NSLOCTEXT("MyModule", "DebugTooltip", "Shows debug info for my camera system");
DebugCategory.IconImage = FSlateIcon(FAppStyle::GetAppStyleSetName(), "ClassIcon.Actor");

EditorModule.RegisterDebugCategory(DebugCategory);

// 可选：注册自定义调试面板
FOnCreateDebugCategoryPanel CreatePanelDelegate;
CreatePanelDelegate.BindLambda([](const FString& CategoryName) -> TSharedRef<SWidget>
{
    return SNew(STextBlock).Text(FText::FromString(TEXT("My Debug Panel")));
});
EditorModule.RegisterDebugCategoryPanel(TEXT("MyCameraDebug"), CreatePanelDelegate);
```

### 进阶用法 — 配置 ObjectTreeGraph

```cpp
// 来源: Public/Editors/ObjectTreeGraphConfig.h
FObjectTreeGraphConfig GraphConfig;
GraphConfig.GraphName = FName("MyCameraGraph");
GraphConfig.DefaultGraphNodeTitleColor = FLinearColor(0.1f, 0.1f, 0.1f);
GraphConfig.DefaultGraphNodeBodyTintColor = FLinearColor(0.05f, 0.05f, 0.05f);

// 注册可连接的类
GraphConfig.ConnectableObjectClasses.Add(UMyCameraNode::StaticClass());
GraphConfig.ConnectableObjectClasses.Add(UMyBlendNode::StaticClass());

// 排除特定类
GraphConfig.NonConnectableObjectClasses.Add(UMyInternalNode::StaticClass());

// 为特定类配置节点行为
FObjectTreeGraphClassConfig& NodeConfig = GraphConfig.ObjectClassConfigs.Add(
    UMyCameraNode::StaticClass(), FObjectTreeGraphClassConfig()
);

// 配置节点外观
NodeConfig.NodeTitleColor(FLinearColor(0.2f, 0.5f, 0.8f));
NodeConfig.NodeTitleTextColor(FLinearColor::White);
NodeConfig.NodeBodyTintColor(FLinearColor(0.02f, 0.02f, 0.05f));

// 配置 self pin
NodeConfig.HasSelfPin(true);
NodeConfig.SelfPinName(FName("CameraInput"));
NodeConfig.SelfPinFriendlyName(NSLOCTEXT("CameraGraph", "SelfPin", "Camera Input"));

// 配置可删除/可复制
NodeConfig.CanCreateNew(true);
NodeConfig.CanDelete(true);

// 配置显示名称处理
NodeConfig.NodeTitleUsesObjectName(true);
NodeConfig.OnGetObjectClassDisplayName.BindLambda([](const UClass* InClass) -> FText
{
    return InClass->GetDisplayNameText();
});

// 禁止为某个类创建/删除（仅作为根节点）
FObjectTreeGraphClassConfig& RootConfig = GraphConfig.ObjectClassConfigs.Add(
    URootCameraNode::StaticClass(), FObjectTreeGraphClassConfig()
);
RootConfig.OnlyAsRoot();

// 剥离显示名称后缀
NodeConfig.StripDisplayNameSuffix(TEXT("Node"));
NodeConfig.StripDisplayNameSuffixes({ TEXT("Node"), TEXT("Camera") });

// 自定义属性 pin 方向
NodeConfig.SetPropertyPinDirectionOverride(FName("BlendTarget"), EGPD_Output);
```

### 进阶用法 — 自定义图表 Schema

```cpp
// 来源: Public/Editors/CameraObjectGraphSchemaBase.h
UCLASS()
class UMyCameraGraphSchema : public UCameraObjectGraphSchemaBase
{
    GENERATED_BODY()

protected:
    virtual void OnBuildGraphConfig(FObjectTreeGraphConfig& InOutGraphConfig) const override
    {
        // 配置自定义图表行为
        InOutGraphConfig.ConnectableObjectClasses.Add(UMyCameraNode::StaticClass());
        
        FObjectTreeGraphClassConfig NodeConfig;
        NodeConfig.NodeTitleColor(FLinearColor::Green);
        InOutGraphConfig.ObjectClassConfigs.Add(UMyCameraNode::StaticClass(), NodeConfig);
    }
};
```

### 进阶用法 — LiveEdit 系统

```cpp
// 来源: Private/GameplayCamerasLiveEditManager.h
// 注册资产包监听器
TSharedPtr<IGameplayCamerasLiveEditManager> LiveEditManager = GetLiveEditManager();
LiveEditManager->AddListener(MyAssetPackage, MyListener);

// 注册 CameraNode 监听器
LiveEditManager->AddListener(MyCameraNode, MyNodeListener);

// 资产构建后通知
LiveEditManager->NotifyPostBuildAsset(MyAssetPackage);

// 属性修改后通知
LiveEditManager->NotifyPostEditChangeProperty(MyCameraNode, PropertyChangedEvent);
```

---

## Demo 示例

### 最小可编译示例 — 自定义 CameraObjectGraphSchema

```cpp
// MyCameraGraphSchema.h
#pragma once

#include "Editors/CameraObjectGraphSchemaBase.h"
#include "MyCameraGraphSchema.generated.h"

UCLASS()
class UMyCameraGraphSchema : public UCameraObjectGraphSchemaBase
{
    GENERATED_BODY()

protected:
    virtual void OnBuildGraphConfig(FObjectTreeGraphConfig& InOutGraphConfig) const override
    {
        Super::OnBuildGraphConfig(InOutGraphConfig);

        // 配置图表的可连接类
        InOutGraphConfig.GraphName = FName("MyCameraNodeGraph");
        InOutGraphConfig.GraphDisplayInfo.PlainName = FText::FromString(TEXT("My Camera Node Graph"));
        InOutGraphConfig.GraphDisplayInfo.DisplayName = FText::FromString(TEXT("My Camera Node Graph"));
    }
};
```

```cpp
// MyCameraGraphSchema.cpp
#include "MyCameraGraphSchema.h"

// 无需额外实现，基类已处理大部分逻辑
// OnBuildGraphConfig 提供子类自定义入口
```

### 最小可编译示例 — 创建并使用 CameraRig 编辑器

```cpp
// MyCameraRigEditorHelper.h
#pragma once

#include "CoreMinimal.h"

class UCameraRigAsset;

namespace UE::Cameras
{

class FMyCameraRigEditorHelper
{
public:
    /** Open a camera rig asset in its dedicated editor. */
    static void OpenCameraRigEditor(UCameraRigAsset* InCameraRig);
};

}  // namespace UE::Cameras
```

```cpp
// MyCameraRigEditorHelper.cpp
#include "MyCameraRigEditorHelper.h"
#include "IGameplayCamerasEditorModule.h"
#include "CameraRigAsset.h"

namespace UE::Cameras
{

void FMyCameraRigEditorHelper::OpenCameraRigEditor(UCameraRigAsset* InCameraRig)
{
    if (!InCameraRig)
    {
        return;
    }

    IGameplayCamerasEditorModule& EditorModule = IGameplayCamerasEditorModule::Get();
    EditorModule.CreateCameraRigEditor(
        EToolkitMode::Standalone,
        TSharedPtr<IToolkitHost>(),
        InCameraRig
    );
}

}  // namespace UE::Cameras
```

---

## 模块依赖

### GameplayCameras（运行时）

从代码结构推断，运行时模块提供：
- 摄像机评估框架
- CameraAsset/CameraRig/Shake 资产类
- CameraVariable 系统
- GameplayCameraComponent

| 模块 | 用途 |
|---|---|
| `EnhancedInput`（插件依赖） | 输入系统集成，摄像机输入绑定 |

无特殊模块依赖（仅标准 Core/Engine 等）。

### GameplayCamerasEditor（编辑器）

从代码结构推断，编辑器模块依赖：

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 核心运行时模块（资产类型定义） |
| `TraceServices`（推断） | UnInsights 追踪集成 |
| `SequencerCore` / `MovieScene`（推断） | Sequencer 轨道编辑器集成 |
| `PropertyEditor`（常见，已省略） | 属性自定义 |
| `GraphEditor`（常见，已省略） | 图表编辑器框架 |

> **注意**：由于未提供 Build.cs 文件内容，以上依赖基于代码分析推断。实际依赖请查看 [GameplayCamerasEditor.Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Cameras/GameplayCameras/Source/GameplayCamerasEditor/GameplayCamerasEditor.Build.cs)。

---

## 编辑器设置

插件提供了 `UGameplayCamerasEditorSettings`（继承自 `UDeveloperSettings`），可在 **项目设置 → Gameplay Cameras Editor** 中配置：

| 设置项 | 类型 | 说明 |
|---|---|---|
| `CameraNodeTitleColor` | FLinearColor | 普通摄像机节点标题颜色 |
| `CameraAssetTitleColor` | FLinearColor | CameraAsset 根节点标题颜色 |
| `CameraRigAssetTitleColor` | FLinearColor | CameraRigAsset 根节点标题颜色 |
| `CameraShakeAssetTitleColor` | FLinearColor | CameraShakeAsset 根节点标题颜色 |
| `CameraRigTransitionTitleColor` | FLinearColor | 过渡节点标题颜色 |
| `CameraRigTransitionConditionTitleColor` | FLinearColor | 过渡条件节点标题颜色 |
| `CameraBlendNodeTitleColor` | FLinearColor | 混合节点标题颜色 |
| `bEnableRunInEditor` | bool | 全局启用/禁用编辑器中运行摄像机装备 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 中摄像机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为部分追踪通道添加或更新描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | GameplayCameras 常规更新 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到新的 UE_LOGF 格式 |

### 维护评价

**积极维护中** ✅

- **创建于 2020 年**，约 6 年历史，是 UE5 摄像机系统的重大架构升级
- **最近更新非常活跃**：最近一个月内有多次实质性提交（Bug 修复、追踪改进、API 迁移）
- 标记为 **实验性**（IsExperimentalVersion=true），API 可能发生 breaking changes
- 默认启用（EnabledByDefault=true），说明 Epic 认为其已达到可用状态
- 由 **Epic Games 官方**维护，是引擎级功能而非社区插件
- 729 个源文件的规模表明这是一个**长期战略项目**，不太可能被废弃
- 依赖 EnhancedInput 插件，表明其与 UE5 新一代输入系统深度集成

**使用建议**：
- ✅ 适合新项目采用，特别是需要复杂摄像机行为的游戏
- ⚠️ 注意实验性标签，升级引擎版本时可能需要适配 API 变更
- ⚠️ 由于标记为实验性，生产环境使用前需充分测试

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [运行时模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras/Source/GameplayCameras)
- [编辑器模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras/Source/GameplayCamerasEditor)
- [插件描述文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Cameras/GameplayCameras/GameplayCameras.uplugin)