# Performance Capture Workflow

> Performance Capture In-Editor Workflow tools. Provides access to the Mocap Manager panel.

| 属性 | 值 |
|---|---|
| 中文名 | 动捕工作流 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产、UI面板、工作流模板） |
| 模块 | `PerformanceCaptureWorkflow` (Runtime), `PerformanceCaptureWorkflowRuntime` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow) | |

## 用途

这是一个面向虚拟制片流程中**动作捕捉录制与管理**的编辑器内工作流插件。它解决了以下核心问题：

1. **动捕会话管理**：提供完整的 Production → Session → Take → Slate 层级化数据库系统，用于组织和追踪所有动捕录制数据
2. **文件夹模板系统**：通过可配置的 Token 化模板（`UPCapSessionTemplate`）自动生成标准化的会话文件夹结构，避免手动创建和命名错误
3. **数据资产封装**：用 `UPCapPerformerDataAsset`（演员）、`UPCapCharacterDataAsset`（角色）、`UPCapPropDataAsset`（道具）封装动捕所需的全部资产引用，支持从内容浏览器一键拖拽生成 Actor
4. **Mocap Manager 面板**：提供基于 MVVM 架构的可定制编辑器 UI 面板，用户可以自定义多个工作流阶段（Phase）
5. **Live Link 集成**：追踪 Live Link Subject 状态变化，为动捕录制提供实时数据流事件通知
6. **Take Recorder 集成**：通过 Session Template 配置录制时钟源、时间码、子序列等参数

简而言之：它把"一次动作捕捉拍摄"涉及的所有环节（项目、会话、演员、角色、道具、录制设置、文件组织）统一到编辑器面板中管理。

## 使用场景

- 你在做虚拟制片项目，需要用 Live Link 进行全身动作捕捉并录制大量 Take → 用 Mocap Manager 管理整个录制流程
- 你的动捕团队需要标准化的文件夹结构和命名规范 → 用 Session Template 定义 Token 化模板
- 你需要将动捕演员（Performer）映射到不同的虚拟角色（Character），并追踪每个 Take 的状态和评级 → 用 PCap 数据资产系统
- 你需要自定义 Mocap Manager 面板的工作流阶段 → 用 `UPCapWorkflowCustomization` 定义 Phase

## 蓝图用法

### 核心节点 — 子系统与设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDatabaseHelper` | 获取数据库助手对象 | `UPerformanceCaptureSubsystem` |
| `GetViewModelCollection` | 获取 MVVM ViewModel 集合 | `UPerformanceCaptureSubsystem` |
| `GetPerformanceCaptureSettings` | 获取插件设置单例 | `UPerformanceCaptureSettings` |
| `ShowPerformanceCaptureProjectSettings` | 打开项目设置面板的 PCap 部分 | `UPerformanceCaptureSettings` |
| `SetSessionTable` | 设置会话数据表引用 | `UPerformanceCaptureSettings` |
| `SetProductionTable` | 设置制作数据表引用 | `UPerformanceCaptureSettings` |
| `SetDefaultSessionTemplate` | 设置默认会话模板 | `UPerformanceCaptureSettings` |

### 核心节点 — 数据表操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddTableRow` | 添加一行新记录 | `UPCapDataTable` |
| `RemoveTableRow` | 删除指定行 | `UPCapDataTable` |
| `DuplicateTableRow` | 复制一行记录 | `UPCapDataTable` |
| `InsertTableRow` | 在指定行上方/下方插入新行 | `UPCapDataTable` |
| `UpdateTableRow` | 原地更新一行数据（保持行顺序） | `UPCapDataTable` |

### 核心节点 — 会话模板

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRootFolder` | 设置模板根文件夹并刷新所有字段 | `UPCapSessionTemplate` |
| `GetRootFolder` | 获取模板根文件夹路径 | `UPCapSessionTemplate` |
| `SetSessionName` | 设置会话名称（自动清理非法字符） | `UPCapSessionTemplate` |
| `GetSessionName` | 获取会话名称 | `UPCapSessionTemplate` |
| `SetProductionName` | 设置制作名称（自动清理非法字符） | `UPCapSessionTemplate` |
| `GetProductionName` | 获取制作名称 | `UPCapSessionTemplate` |
| `UpdateAllFields` | 强制刷新所有 Token 化字段 | `UPCapSessionTemplate` |

### 核心节点 — 工具函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Sanitize File Name String` | 清理字符串中的非法文件名字符 | `UPerformanceCaptureBPFunctionLibrary` |
| `Sanitize File Path String` | 清理字符串中的非法字符（保留路径分隔符） | `UPerformanceCaptureBPFunctionLibrary` |
| `Get All Actors With Component` | 查找世界中所有包含指定组件的 Actor | `UPerformanceCaptureBPFunctionLibrary` |

### 核心节点 — 可视化

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateColor` | 更新骨骼可视化器的颜色 | `UPCapBoneVisualiser` |

### 核心节点 — 委托（事件）

`UPerformanceCaptureSubsystem` 提供大量 BlueprintAssignable 事件委托：

| 委托 | 说明 |
|---|---|
| `OnPCapAssetRemoved` | 资产从注册表移除时触发 |
| `OnPCapAssetRenamed` | 资产重命名时触发 |
| `OnPCapAssetAdded` | 新资产添加时触发 |
| `OnPCapActorModified` | 关卡编辑器中 Actor 被修改时触发 |
| `OnPCapEditorUndo` / `OnPCapEditorRedo` | 编辑器撤销/重做时触发 |
| `OnPCapAssetEditorOpen` / `OnPCapAssetEditorClose` | 资产编辑器打开/关闭时触发 |
| `OnPCapLiveLinkSubjectUpdate` | Live Link Subject 状态更新时触发 |
| `OnPCapLiveLinkSubjectAdded` / `OnPCapLiveLinkSubjectRemoved` | Live Link Subject 添加/移除时触发 |
| `OnPCapLiveLinkSubjectEnableChanged` | Live Link Subject 启用状态变化时触发 |
| `OnPCapTimecodeProviderChanged` | 时间码提供者变化时触发 |
| `OnPCapCustomTimestepProviderChanged` | 自定义时间步提供者变化时触发 |

### 使用示例（蓝图描述）

**创建一个新会话并记录 Take：**

1. 获取 `UPerformanceCaptureSettings` 设置单例，确认 SessionTable 和 DefaultSessionTemplate 已配置
2. 获取 `UPerformanceCaptureSubsystem`，通过 `GetDatabaseHelper` 获取数据库助手
3. 创建 `UPCapPerformerDataAsset` 数据资产，配置 LiveLinkSubject、PerformerActorClass、BaseSkeletalMesh
4. 创建 `UPCapCharacterDataAsset`，引用 Performer 资产，配置 SkeletalMesh 和 IKRig
5. 创建 `UPCapSessionTemplate`，设置 ProductionName 和 SessionName，Token 化字段会自动生成最终路径
6. 在 Mocap Manager 面板中选择会话，添加 Slate 记录（`FPCapSlateRecord`），设置状态为 Incomplete
7. 开始录制，完成后系统自动创建 `FPCapTakeRecord` 记录，包含时间码、帧率、时长等信息
8. 对 Take 设置评级（Rating 0-5）和状态（ThumbsUp/ThumbsDown/Neutral）

## C++ 用法

### 头文件引入

```cpp
#include "PCapDatabase.h"
#include "PCapSubsystem.h"
#include "PCapSettings.h"
#include "PCapSessionTemplate.h"
#include "PCapDataTable.h"
```

### 基本用法 — 获取子系统与设置

```cpp
// 来源: PCapSubsystem.h, PCapSettings.h

// 获取 PCap 子系统（引擎子系统，编辑器启动时自动初始化）
UPerformanceCaptureSubsystem* Subsystem = GEngine->GetEngineSubsystem<UPerformanceCaptureSubsystem>();
UMVVMViewModelCollectionObject* ViewModelCollection = Subsystem->GetViewModelCollection();

// 获取项目设置
UPerformanceCaptureSettings* Settings = UPerformanceCaptureSettings::GetPerformanceCaptureSettings();
UPCapSessionTemplate* DefaultTemplate = Settings->DefaultSessionTemplate.Get();
```

### 基本用法 — 数据表操作

```cpp
// 来源: PCapDataTable.h

UPCapDataTable* SessionTable = Settings->SessionTable.Get();

// 添加一行
SessionTable->AddTableRow("Session_001");

// 更新一行（保持行顺序）
FPCapSessionRecord SessionData;
SessionData.SessionName = "Day01_Morning";
SessionData.SessionDateTime = FDateTime::Now();
SessionData.ProductionName = "MyProduction";
SessionTable->UpdateTableRow("Session_001", SessionData);

// 复制一行
SessionTable->DuplicateTableRow("Session_001", "Session_001_Copy");

// 删除一行
SessionTable->RemoveTableRow("Session_001_Copy");
```

### 进阶用法 — 监听资产和 Live Link 事件

```cpp
// 来源: PCapSubsystem.h

UPerformanceCaptureSubsystem* Subsystem = GEngine->GetEngineSubsystem<UPerformanceCaptureSubsystem>();

// 监听资产变化
Subsystem->OnPCapAssetAdded.AddDynamic(this, &UMyClass::HandleAssetAdded);
Subsystem->OnPCapAssetRemoved.AddDynamic(this, &UMyClass::HandleAssetRemoved);

// 监听 Live Link Subject 状态
Subsystem->OnPCapLiveLinkSubjectUpdate.AddDynamic(this, &UMyClass::HandleLiveLinkUpdate);
Subsystem->OnPCapTimecodeProviderChanged.AddDynamic(this, &UMyClass::HandleTimecodeChanged);

// 处理函数示例
void UMyClass::HandleAssetAdded(FAssetData NewAsset)
{
    UE_LOG(LogPCap, Log, TEXT("New PCap asset added: %s"), *NewAsset.AssetName.ToString());
}

void UMyClass::HandleLiveLinkUpdate(FLiveLinkSubjectKey Subject, ELiveLinkSubjectState State)
{
    // 根据 Live Link Subject 状态更新 UI 或录制逻辑
}
```

### 进阶用法 — 自定义 Session Template Token

```cpp
// 来源: PCapSessionTemplate.h, PCapNamingTokens.h

// Session Template 支持 Token 化的文件夹路径和字符串
// PCap 命名空间可用 Token:
//   {session}           - 会话名称
//   {production}        - 制作名称
//   {sessionToken}      - Session Token 字段的输出值
//   {pcapRootFolder}    - PCap 根文件夹
//   {sessionFolder}     - 会话文件夹路径
// 全局 Token:
//   {yyyy}/{yy}         - 年份
//   {mm}/{Mmm}/{MMM}    - 月份
//   {dd}/{Ddd}/{DDD}    - 日期
//   {24h}/{12h}         - 小时
//   {min}/{sec}/{ms}    - 分钟/秒/毫秒
```

## Demo 示例

```cpp
// MyPCapManager.h
#pragma once

#include "CoreMinimal.h"
#include "PCapDatabase.h"
#include "PCapSubsystem.h"
#include "PCapSettings.h"
#include "PCapDataTable.h"
#include "MyPCapManager.generated.h"

UCLASS(BlueprintType)
class UMyPCapManager : public UObject
{
    GENERATED_BODY()

public:
    /** 创建一个制作并添加会话 */
    UFUNCTION(BlueprintCallable, Category = "MyPCap")
    void CreateProductionAndSession();

    /** 监听 PCap 事件 */
    UFUNCTION(BlueprintCallable, Category = "MyPCap")
    void StartListening();

private:
    UFUNCTION()
    void OnTakeCreated(FAssetData NewAsset);

    UPROPERTY()
    TWeakObjectPtr<UPerformanceCaptureSubsystem> CachedSubsystem;
};
```

```cpp
// MyPCapManager.cpp
#include "MyPCapManager.h"
#include "PCapSessionTemplate.h"

void UMyPCapManager::CreateProductionAndSession()
{
    UPerformanceCaptureSettings* Settings = UPerformanceCaptureSettings::GetPerformanceCaptureSettings();
    if (!Settings)
    {
        return;
    }

    // 获取制作数据表并添加记录
    UPCapDataTable* ProdTable = Settings->ProductionTable.Get();
    if (ProdTable)
    {
        ProdTable->AddTableRow("Production_001");

        FPCapProductionRecord ProdRecord;
        ProdRecord.ProductionName = "MyShow";
        ProdRecord.ProductionNotes = "Pilot episode mocap sessions";
        ProdTable->UpdateTableRow("Production_001", ProdRecord);
    }

    // 获取会话数据表并添加记录
    UPCapDataTable* SessionTable = Settings->SessionTable.Get();
    if (SessionTable)
    {
        SessionTable->AddTableRow("Session_001");

        FPCapSessionRecord SessionRecord;
        SessionRecord.SessionName = "Day01_Morning";
        SessionRecord.SessionDateTime = FDateTime::Now();
        SessionRecord.ProductionName = "MyShow";
        SessionRecord.ProductionUID = ProdRecord.UID;
        SessionRecord.SessionNotes = "First session of the day";
        SessionRecord.bIsWorldPartition = false;
        SessionTable->UpdateTableRow("Session_001", SessionRecord);
    }

    // 添加 Take 记录
    UPCapDataTable* TakesTable = SessionRecord.TakesDataTable.Get();
    if (TakesTable)
    {
        TakesTable->AddTableRow("Take_001");

        FPCapTakeRecord TakeRecord;
        TakeRecord.DateTimeCreated = FDateTime::Now();
        TakeRecord.TakeStatus = EPCapTakeStatus::Neutral;
        TakeRecord.Rating = 0;
        TakeRecord.bContainsLiveLinkSources = true;
        TakeRecord.Framerate = FFrameRate(30, 1);
        TakesTable->UpdateTableRow("Take_001", TakeRecord);
    }
}

void UMyPCapManager::StartListening()
{
    CachedSubsystem = GEngine->GetEngineSubsystem<UPerformanceCaptureSubsystem>();
    if (CachedSubsystem.IsValid())
    {
        CachedSubsystem->OnPCapAssetAdded.AddDynamic(this, &UMyPCapManager::OnTakeCreated);
    }
}

void UMyPCapManager::OnTakeCreated(FAssetData NewAsset)
{
    UE_LOG(LogPCap, Log, TEXT("New PCap asset: %s"), *NewAsset.AssetName.ToString());
}
```

## 模块依赖

从源码头文件分析，该插件依赖以下非常见模块：

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link Subject 跟踪（FPCapTakeRecord、FPCapPerformerDataAsset） |
| `ModelViewViewModel` | MVVM 架构支持（UPCapViewmodel、UMVVMViewModelCollectionObject） |
| `IKRig` | IK Rig 和 Retargeter 引用（UIKRigDefinition、UIKRetargeter） |
| `LevelSequence` | 关卡序列引用（ULevelSequence） |
| `TakeRecorder` | Take Recorder 录制参数集成（时钟源、时间码配置） |
| `NamingTokens` | Token 化命名系统（UNamingTokens） |
| `DataLayer` | World Partition 数据层支持（UDataLayerAsset） |
| `EditorWidgets` | Editor Utility Widget 面板支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `6738ae86` | [Performance Capture Workflow] - Add telemetry to the Mocap Manager panel invocation. | 为 Mocap Manager 面板添加了遥测功能 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 重组了虚拟制片资产的分类目录结构 |
| 2026-05-12 | `cb548ae0` | [Performance Capture Workflow] - Add multicast BP delegates that fire on changes to the timecode and | 新增时间码和时间步提供者变化的蓝图委托事件 |
| 2026-05-01 | `e5ecc8a9` | [PerformanceCaptureWorkflow] - Adds editor only BP function to update a specific row in a PCapDataTa | 新增 UpdateTableRow 蓝图函数，支持原地更新数据表行 |
| 2026-04-20 | `12bc1b78` | [PerformanceCaptureWorkflow] | 更新详情被截断，为插件的一次常规更新 |

### 维护评价

- **创建时间**：2025-04-02，插件非常新（不到 1 年）
- **版本状态**：`IsBetaVersion = true`，版本号 0.2，处于 Beta 阶段
- **更新频率**：活跃维护中，最近一个月有多次功能性更新（遥测、新委托、新 API）
- **已知限制**：
  - 数据库助手（`UPerformanceCaptureDatabaseHelper`）目前是蓝图可实现的存根，注释标记为 `TODO currently a stub and not yet implemented`
  - `Installed: false`，需要手动启用
  - 第二个模块 `PerformanceCaptureWorkflowRuntime` 的具体实现未在提供的源码中展示
- **推荐程度**：如果你的项目涉及虚拟制片中的动作捕捉流程，这是一个值得尝试的 Beta 插件。Epic Games 正在积极维护，API 在快速迭代中，注意可能有破坏性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PerformanceCaptureWorkflow)
- 官方文档：暂无
- 测试用例：未在插件目录内发现测试文件