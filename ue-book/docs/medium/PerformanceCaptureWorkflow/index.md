# Performance Capture Workflow

> Performance Capture In-Editor Workflow tools. Provides access to the Mocap Manager panel.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图 UI、Stage 资产、材质、数据表模板） |
| 模块 | `PerformanceCaptureWorkflow` (Editor), `PerformanceCaptureWorkflowRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow) | |

## 用途

Performance Capture Workflow（简称 PCap）是 Epic Games 为 UE5 编辑器开发的**动捕（Motion Capture）工作流管理工具**。它解决的核心问题是：在虚拟制片环境中，如何将动捕录制的整个流程——从项目创建、Session 管理、演员/角色/道具数据管理、Take Recorder 集成、到最终的资产组织——全部整合到编辑器内完成。

该插件提供了 **Mocap Manager** 面板，这是一个基于 Editor Utility Widget (CommonUI + MVVM) 构建的自定义 UI，用于管理整个动捕会话。它与 UE5 的 Live Link、Take Recorder、IK Rig 系统深度集成，让动捕操作员可以在一个统一界面中完成所有操作，而不需要在多个编辑器窗口之间切换。

**关键特性：**
- 基于 Session Template 的自动文件夹结构创建
- Production → Session → Take 三级数据管理体系
- Live Link 数据实时预览和录制
- 动捕演员（Performer）、角色（Character）、道具（Prop）的数据资产管理
- 支持 Level Streaming 和 World Partition 两种关卡模式
- 通过命名令牌（Naming Tokens）实现灵活的资产命名
- 支持 Multi-User 编辑

## 使用场景

- 你在使用 Vicon、OptiTrack 等光学动捕系统进行虚拟制片 → 用 PerformanceCaptureWorkflow 管理整个录制流程
- 你需要在 UE 编辑器内实时预览动捕数据并录制 Take → 该插件通过 Mocap Manager 面板提供一站式操作
- 你需要为多个演员和角色管理复杂的 IK Retarget 设置 → PCap 的 Performer/Character DataAsset 体系帮你组织
- 你的项目需要标准化的文件夹结构来管理动捕资产 → Session Template 自动创建规范的目录结构
- 你需要使用道具（如手持武器、工具）进行动捕 → Prop Component 支持 Live Link 驱动的道具追踪

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPerformanceCaptureSettings` | 获取 PCap 项目设置对象 | `UPerformanceCaptureSettings` |
| `ShowPerformanceCaptureProjectSettings` | 打开项目设置面板并跳转到 PCap 配置页 | `UPerformanceCaptureSettings` |
| `SetSessionTable` | 设置 Session 数据表 | `UPerformanceCaptureSettings` |
| `SetProductionTable` | 设置 Production 数据表 | `UPerformanceCaptureSettings` |
| `SetDefaultSessionTemplate` | 设置默认 Session Template | `UPerformanceCaptureSettings` |
| `GetDatabaseHelper` | 获取数据库辅助对象 | `UPerformanceCaptureSubsystem` |
| `GetViewModelCollection` | 获取 MVVM ViewModel 集合 | `UPerformanceCaptureSubsystem` |
| `SanitizeFileString` | 清理文件名中的非法字符 | `UPerformanceCaptureBPFunctionLibrary` |
| `SanitizePathString` | 清理文件路径中的非法字符（保留路径分隔符） | `UPerformanceCaptureBPFunctionLibrary` |
| `GetAllActorsWithComponent` | 查找世界中包含指定组件的所有 Actor | `UPerformanceCaptureBPFunctionLibrary` |

### DataTable 操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddTableRow` | 向数据表添加新行 | `UPCapDataTable` |
| `RemoveTableRow` | 从数据表删除指定行 | `UPCapDataTable` |
| `DuplicateTableRow` | 复制数据表中的行 | `UPCapDataTable` |
| `InsertTableRow` | 在指定行的上方或下方插入新行 | `UPCapDataTable` |
| `OnDatatableModified` | 数据表修改时触发的委托 | `UPCapDataTable` |

### Prop Component 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLiveLinkSubject` | 设置道具的 Live Link Subject | `UPCapPropComponent` |
| `GetLiveLinkSubject` | 获取当前 Live Link Subject | `UPCapPropComponent` |
| `SetEvaluateLiveLinkData` | 启用/禁用 Live Link 数据评估 | `UPCapPropComponent` |
| `GetEvaluateLiveLinkData` | 获取 Live Link 评估状态 | `UPCapPropComponent` |
| `SetOffsetTransform` | 设置道具的本地空间偏移 | `UPCapPropComponent` |
| `SetControlledComponent` | 设置被控制的场景组件 | `UPCapPropComponent` |
| `GetControlledComponent` | 获取被控制的场景组件 | `UPCapPropComponent` |
| `CalculateDynamicOffset` | 计算动态约束偏移（蓝图可实现事件） | `UPCapPropComponent` |

### Runtime 函数库节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSourceRig` | 从 IKRetargeter 获取源 IK Rig | `UPCapWorkflowRuntimeFunctionLibrary` |
| `GetTargetRig` | 从 IKRetargeter 获取目标 IK Rig | `UPCapWorkflowRuntimeFunctionLibrary` |
| `GetRetargetChains` | 获取 IK Rig 中的所有骨骼链 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `GetChainStartBone` | 获取骨骼链的起始骨骼名 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `GetChainEndBone` | 获取骨骼链的结束骨骼名 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `GetChainFromBone` | 根据骨骼名查找其所属的骨骼链 | `UPCapWorkflowRuntimeFunctionLibrary` |
| `GetChainPair` | 获取对应的源/目标骨骼链 | `UPCapWorkflowRuntimeFunctionLibrary` |

### Prop AnimInstance 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSubject` | 设置道具的 Live Link Subject | `UPCapPropLiveLinkAnimInstance` |
| `EnableLiveLinkEvaluation` | 启用/禁用 Live Link 评估 | `UPCapPropLiveLinkAnimInstance` |
| `SetOffsetTransform` | 设置偏移变换 | `UPCapPropLiveLinkAnimInstance` |
| `SetDynamicConstraintVector` | 设置动态约束向量 | `UPCapPropLiveLinkAnimInstance` |

### Bone Visualizer 节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateColor` | 更新骨骼可视化器的颜色 | `UPCapBoneVisualiser` |

### Subsystem 委托

`UPerformanceCaptureSubsystem` 暴露了多个蓝图可绑定的委托，用于响应编辑器事件：

| 委托 | 参数 | 说明 |
|---|---|---|
| `OnPCapAssetRemoved` | `FAssetData` | 资产从注册表移除时触发 |
| `OnPCapAssetRenamed` | `FAssetData, FString` | 资产重命名时触发 |
| `OnPCapAssetAdded` | `FAssetData` | 新资产添加时触发 |
| `OnPCapActorModified` | `AActor*` | 关卡编辑器中的 Actor 被修改时触发 |
| `OnPCapEditorUndo` | `bool` | 用户执行 Undo 时触发 |
| `OnPCapEditorRedo` | `bool` | 用户执行 Redo 时触发 |
| `OnPCapAssetEditorOpen` | `UObject*` | 资产编辑器打开时触发 |
| `OnPCapAssetEditorClose` | `UObject*` | 资产编辑器关闭时触发 |
| `OnPCapLiveLinkSubjectUpdate` | `FLiveLinkSubjectKey, ELiveLinkSubjectState` | Live Link Subject 状态更新时触发 |
| `OnPCapLiveLinkSubjectAdded` | `FLiveLinkSubjectKey` | Live Link Subject 添加时触发 |
| `OnPCapLiveLinkSubjectRemoved` | `FLiveLinkSubjectKey` | Live Link Subject 移除时触发 |
| `OnPCapLiveLinkSubjectEnableChanged` | `FLiveLinkSubjectKey, bool` | Live Link Subject 启用状态变化时触发 |

### 使用示例（蓝图描述）

**配置项目设置：**
1. 打开 Project Settings → Plugins → Performance Capture
2. 设置 `Stage Root Actor Class`（舞台根 Actor 类）
3. 设置 `Default Performer Mesh`（默认演员骨骼网格）
4. 设置 `Mocap Manager UI`（Mocap Manager 的 Editor Utility Widget 蓝图）
5. 设置 `ViewModel Class`（MVVM ViewModel 蓝图类）
6. 设置 `Default Session Template`（默认 Session 模板）

**创建道具组件：**
1. 创建一个 Static Mesh Actor
2. 添加 `PCapPropComponent`（蓝图中搜索 "Prop Component"）
3. 设置 `SubjectName` 为对应的 Live Link Subject
4. 可选：设置 `OffsetTransform` 调整道具位置
5. 可选：启用 `bUseDynamicConstraint` 并配置动态约束

## C++ 用法

### 头文件引入

```cpp
// Editor 模块
#include "PerformanceCapture.h"
#include "PCapSettings.h"
#include "PCapSubsystem.h"
#include "PCapDatabase.h"
#include "PCapBPFunctionLibrary.h"

// Runtime 模块
#include "PCapPropComponent.h"
#include "PCapStageRoot.h"
#include "PCapWorkflowRuntimeFunctionLibrary.h"
```

### 基本用法 - 获取 Subsystem 和设置

```cpp
// 获取 PCap 子系统（引擎级别）
UPerformanceCaptureSubsystem* PCapSubsystem = GEngine->GetEngineSubsystem<UPerformanceCaptureSubsystem>();

// 获取数据库辅助对象
UPerformanceCaptureDatabaseHelper* DBHelper = PCapSubsystem->GetDatabaseHelper();

// 获取项目设置
const UPerformanceCaptureSettings* Settings = UPerformanceCaptureSettings::GetPerformanceCaptureSettings();

// 获取舞台根 Actor 类
UClass* StageRootClass = Settings->StageRoot.LoadSynchronous();
```
*来源: `PCapSubsystem.cpp` - `OnEngineInitComplete()`*

### 基本用法 - 数据表操作

```cpp
// 创建数据表行
UPCapDataTable* DataTable = ...;
DataTable->AddTableRow(FName("NewRow"));

// 复制行
DataTable->DuplicateTableRow(FName("SourceRow"), FName("NewRow"));

// 删除行
DataTable->RemoveTableRow(FName("RowToDelete"));

// 在指定行上方插入
DataTable->InsertTableRow(FName("SelectedRow"), FName("InsertedRow"), true);

// 监听数据表修改
DataTable->OnDatatableModified.AddDynamic(this, &UMyClass::OnTableChanged);
```
*来源: `PCapDataTable.cpp`*

### 基本用法 - Runtime 函数库

```cpp
// 从 IKRetargeter 获取源/目标 Rig
const UIKRigDefinition* SourceRig = UPCapWorkflowRuntimeFunctionLibrary::GetSourceRig(MyRetargeter);
const UIKRigDefinition* TargetRig = UPCapWorkflowRuntimeFunctionLibrary::GetTargetRig(MyRetargeter);

// 获取骨骼链
TArray<FBoneChain> Chains = UPCapWorkflowRuntimeFunctionLibrary::GetRetargetChains(SourceRig);

// 获取骨骼链的起始和结束骨骼
FName StartBone = UPCapWorkflowRuntimeFunctionLibrary::GetChainStartBone(SourceRig, FName("LeftArm"));
FName EndBone = UPCapWorkflowRuntimeFunctionLibrary::GetChainEndBone(SourceRig, FName("LeftArm"));

// 根据骨骼名查找所属链
FName ChainName = UPCapWorkflowRuntimeFunctionLibrary::GetChainFromBone(SourceRig, FName("LeftHand"));
```
*来源: `PCapWorkflowRuntimeFunctionLibrary.h`*

### 进阶用法 - 命名令牌系统

```cpp
// PCap 使用命名令牌（Naming Tokens）系统来生成动态路径和名称
// 令牌命名空间为 "pcap"，支持以下令牌：
// {session} - Session 名称
// {production} - Production 名称
// {sessionToken} - Session Token 字段的输出值
// {pcapRootFolder} - PCap 根文件夹
// {sessionFolder} - Session 文件夹路径
//
// 也支持全局令牌如 {yyyy}, {mm}, {dd}, {24h}, {min}, {sec} 等
```
*来源: `PCapNamingTokens.h`, `PCapSessionTemplate.h`*

### 进阶用法 - Prop Component 动态约束

```cpp
// Prop Component 支持动态约束，可将道具附加到角色的特定骨骼
// 配置步骤：
// 1. 启用 bUseDynamicConstraint
// 2. 设置 DynamicAttachmentCharacters（目标角色列表）
// 3. 可选设置 DynamicConstraintAttachBones（特定骨骼）
// 4. 重写 CalculateDynamicOffset() 实现自定义偏移计算
```
*来源: `PCapPropComponent.h`*

## Demo 示例

### 最小 Prop Component 使用示例

```cpp
// MyPropActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyPropActor.generated.h"

class UPCapPropComponent;
class UStaticMeshComponent;

UCLASS()
class AMyPropActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPropActor();

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> MeshComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UPCapPropComponent> PropComponent;
};
```

```cpp
// MyPropActor.cpp
#include "MyPropActor.h"
#include "PCapPropComponent.h"
#include "Components/StaticMeshComponent.h"

AMyPropActor::AMyPropActor()
{
    MeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    SetRootComponent(MeshComponent);

    PropComponent = CreateDefaultSubobject<UPCapPropComponent>(TEXT("PropComponent"));
    PropComponent->SubjectName = FName("MyPropSubject");
}
```

```cpp
// YourModule.Build.cs - 依赖配置
PublicDependencyModuleNames.AddRange(new string[]
{
    "PerformanceCaptureWorkflowRuntime"
});
```

## 数据资产体系

PCap 定义了一套完整的数据资产层次结构：

| 资产类 | 说明 | 关键属性 |
|---|---|---|
| `UPCapPerformerDataAsset` | 动捕演员资产 | PerformerName, LiveLinkSubject, BaseSkeletalMesh, IKRig |
| `UPCapCharacterDataAsset` | 角色资产 | CharacterName, SourcePerformerAsset, SkeletalMesh, Retargeter |
| `UPCapPropDataAsset` | 道具资产 | PropName, LiveLinkSubject, PropStaticMesh, PropSkeletalMesh |
| `UPCapSessionTemplate` | Session 模板 | 文件夹结构模板、Take Recorder 配置、命名令牌 |
| `UPCapDataTable` | 数据表 | Production/Session/Take/Slate 记录 |

### 数据库记录结构

| 记录类型 | 说明 | 关键字段 |
|---|---|---|
| `FPCapProductionRecord` | Production 记录 | ProductionName, ProductionNotes |
| `FPCapSessionRecord` | Session 记录 | SessionName, SessionDateTime, 各文件夹路径, Performers, Characters |
| `FPCapTakeRecord` | Take 记录 | RecordedTake (LevelSequence), Framerate, Timecode, TakeStatus, Rating |
| `FPCapSlateRecord` | Slate 记录 | Slate 名称, 备注, 状态(Incomplete/Complete/Skip) |

## 自定义资产定义

插件为以下资产类型注册了自定义的 Asset Definition，在内容浏览器中有独特的显示名称和图标：

| 类 | 显示名称 | 颜色 |
|---|---|---|
| `UAssetDefinition_PCapDataTable` | PCap Data Table | 绿色 (57, 181, 74) |
| `UAssetDefinition_PCapDataAsset` | PCap DataAsset | 紫色 (161, 57, 191) |
| `UAssetDefinition_PerformerDataAsset` | PCap Performer Asset | 自定义图标 |
| `UAssetDefinition_CharacterDataAsset` | PCap Character Asset | 自定义图标 |
| `UAssetDefinition_PropDataAsset` | PCap Prop Asset | 自定义图标 |
| `UAssetDefinition_SessionTemplateAsset` | PCap Session Template | 自定义图标 |

## Actor Factory

插件注册了三个 Actor Factory，支持从内容浏览器直接拖放 DataAsset 到场景中：

| Factory | 说明 |
|---|---|
| `UPCapCharacterActorFactory` | 从 Character DataAsset 生成角色 Actor |
| `UPCapPerformerActorFactory` | 从 Performer DataAsset 生成演员 Actor |
| `UPCapPropActorFactory` | 从 Prop DataAsset 生成道具 Actor |

## 插件依赖

该插件依赖以下其他插件：

| 插件 | 用途 |
|---|---|
| `MultiUserClient` | 多用户协作编辑 |
| `LiveLink` | 实时数据流（动捕数据接收） |
| `PerformanceCaptureCore` | PCap 核心基础模块 |
| `GeometryScripting` | 几何体脚本操作 |
| `CommonUI` | 通用 UI 框架（Mocap Manager 面板） |
| `SkeletalMeshModelingTools` | 骨骼网格建模工具 |
| `EditorScriptingUtilities` | 编辑器脚本工具 |
| `ModelViewViewModel` | MVVM 框架（Mocap Manager UI 架构） |
| `EngineAssetDefinitions` | 资产定义框架 |
| `Takes` | Take Recorder 基础 |
| `DirectoryPlaceholder` | 目录占位符 |
| `NamingTokens` | 命名令牌系统 |
| `IKRig` | IK 绑定和重定向 |
| `LiveLinkUnrealDevice` | Live Link Unreal 设备 |

## 模块依赖

### PerformanceCaptureWorkflow (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础 |
| `CommonUI` | 通用 UI 框架 |
| `PlacementMode` | 放置模式（Actor Factory 拖放） |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `PerformanceCaptureCore` | PCap 核心类型定义 |
| `LiveLink` / `LiveLinkInterface` / `LiveLinkAnimationCore` | Live Link 集成 |
| `IKRig` | IK 绑定 |
| `LevelSequence` | 关卡序列（Take 管理） |
| `ModelViewViewModel` | MVVM 框架 |
| `UMG` / `UMGEditor` | UMG UI |
| `Blutility` | 蓝图工具函数库基类 |
| `EditorSubsystem` | 编辑器子系统 |
| `NamingTokens` | 命名令牌 |
| `TakeRecorderSources` / `TakesCore` | Take Recorder 集成 |
| `CinematicCamera` | 电影摄像机 |
| `AssetDefinition` / `EngineAssetDefinitions` | 资产定义 |
| `DataTableEditor` | 数据表编辑器 |
| `PerformanceCaptureWorkflowRuntime` | 运行时模块 |

### PerformanceCaptureWorkflowRuntime (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `Slate` / `SlateCore` | UI 框架 |
| `LiveLink` / `LiveLinkInterface` / `LiveLinkAnimationCore` | Live Link 集成 |
| `PerformanceCaptureCore` | PCap 核心类型定义 |
| `IKRig` | IK 绑定 |

## Content 内容

插件包含以下 Content 目录：

| 目录 | 用途 |
|---|---|
| `Stage/` | 舞台相关资产（正交视图渲染目标、网格材质） |
| `Visualizers/` | 骨骼可视化相关资产 |
| `Database/` | 数据库模板资产 |
| `Session/` | Session 相关资产 |
| `Common/` | 公共资产 |
| `Core/` | 核心资产 |
| `Delivery/` | 交付相关资产 |
| `Motion/` | 动捕相关资产 |
| `Record/` | 录制相关资产 |
| `Review/` | 审阅相关资产 |

## 维护状态

### 近期更新

1. `40a3e91294ea` | 2025-09-29 | 修改插件依赖顺序，使 MultiUser Client 在 LiveLink 之前加载，修复插件模块间的复杂交叉依赖问题
2. `960852b8712b` | 2025-09-24 | Bughawk 文档字符串修复
3. `dff03cfa67e` | 2025-09-24 | 在文件名和路径清理函数中添加 `<>` 字符过滤，改进函数显示名称

### 维护评价

- **创建时间**：2025-04-02，非常新的插件（约 1 年历史）
- **维护状态**：活跃维护中，最近 3 个月内有多次功能性更新
- **实验性标记**：`IsExperimentalVersion=true`，表明 Epic 仍在积极开发但尚未正式发布
- **版本号**：0.2（处于早期版本阶段）
- **依赖复杂度**：依赖 14 个其他插件，说明这是一个功能丰富但耦合度较高的系统
- **推荐程度**：适合虚拟制片团队使用，但需注意实验性状态可能带来 API 变化

⚠️ **注意**：该插件标记为实验性版本（`IsExperimentalVersion=true`），默认不启用。需要在 Edit → Plugins 中手动启用。API 可能在后续版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow)
- [PerformanceCaptureCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PerformanceCaptureCore)（核心依赖）
- 测试用例：未发现独立测试文件
