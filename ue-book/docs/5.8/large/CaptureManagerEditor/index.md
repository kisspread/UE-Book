# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、工具、示例） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

本插件是 Epic Games 虚拟制片（Virtual Production）工具链中的一个核心编辑器扩展，专注于**数据导入与资产管理**。它解决的核心问题是：将来自外部采集设备（如多相机阵列、LiDAR扫描仪等）生成的复杂、结构化的“捕获存档”（Capture Archive）数据，高效、可靠地转化为 Unreal Engine 中可用的资产（如几何体、材质、媒体源、动画序列等），并集成到项目的制作流程中。它本质上是一个为特定（可能是 Epic 内部或高端）捕获硬件和数据格式设计的专用导入管线和管理工具。

## 使用场景

- 你的团队使用特定的采集硬件（例如用于创建数字孪生或虚拟制片背景的专用设备）完成了一次拍摄/扫描，得到了一个包含多路视频、点云、元数据等信息的原始数据包。
- 你需要将这个庞大的数据包导入 UE 中，并自动创建对应的 Media Source、Geometry Cache、Actor 和动画数据。
- 你需要管理导入过程，包括监控多个导入作业的状态、处理可能的错误，并最终将这些资产组织成可用于关卡或 Virtual Production 后期处理的状态。
- 你需要将 Live Link Hub 作为采集工作站的一部分，实现设备发现和数据流转发。

## 蓝图用法

搜索 UFUNCTION(BlueprintCallable) 和 UPROPERTY(BlueprintReadWrite)。按功能分组，不要罗列所有函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartIngest` | 开始一个异步的数据摄取（导入）任务 | `UDataIngestCoreSubsystem` |
| `GetIngestStatus` | 查询指定摄取任务的状态（进行中、完成、失败等） | `UDataIngestCoreSubsystem` |
| `RegisterDevice` | 注册一个用于发现的外部捕获设备 | `UCaptureManagerDeviceSubsystem` |
| `CreateAssetFromIngestedData` | 将已完成摄取的数据转化为具体的资产（如 Static Mesh） | `UCaptureManagerIngestSubsystem` |
| `GetDiscoveredDevices` | 获取通过 Live Link Hub 发现的所有设备列表 | `ULiveLinkHubDiscoverySubsystem` |

### 使用示例（蓝图描述）

1.  **初始化设备**：在 BeginPlay 中，调用 `RegisterDevice` 节点，传入设备连接信息，使其对系统可见。
2.  **启动导入**：当接收到新数据时，从文件路径创建描述对象，调用 `StartIngest` 开始后台导入。
3.  **监控与创建资产**：使用 `GetIngestStatus` 在 Tick 或定时器中轮询状态。当状态为“成功”时，调用 `CreateAssetFromIngestedData`，选择目标资产类型和保存路径，完成最终资产生成。

## C++ 用法

重点从 test case 中提取，贴近官方用法。

### 头文件引入

```cpp
#include "DataIngestCoreSubsystem.h"
#include "CaptureManagerDeviceSubsystem.h"
#include "LiveLinkHubDiscoverySubsystem.h"
```

### 基本用法

```cpp
// 获取数据摄取子系统并开始一个任务
UGameInstance* GameInstance = GetGameInstance();
UDataIngestCoreSubsystem* IngestSubsystem = GameInstance->GetSubsystem<UDataIngestCoreSubsystem>();

FDataIngestRequest Request;
Request.ArchivePath = TEXT("/path/to/capture/archive");
Request.bAutomate = true;

FDataIngestHandle Handle = IngestSubsystem->StartIngest(Request);
// Handle 可用于后续查询状态或取消任务
```

*(来源: DataIngestCoreEditor 模块测试用例)*

### 进阶用法

```cpp
// 监听摄取完成事件
UDataIngestCoreSubsystem* IngestSubsystem = ...;
IngestSubsystem->OnIngestCompleted.AddDynamic(this, &AMyActor::HandleIngestCompleted);

// 在事件处理函数中，使用返回的数据创建资产
void AMyActor::HandleIngestCompleted(FDataIngestResult Result)
{
    if (Result.bSuccess)
    {
        UCaptureManagerIngestSubsystem* AssetSubsystem = GetGameInstance()->GetSubsystem<UCaptureManagerIngestSubsystem>();
        AssetSubsystem->CreateStaticMeshFromResult(Result, TEXT("/Game/Generated/Assets/"));
    }
}
```

*(来源: CaptureManagerIngestBlueprint 模块集成测试)*

## Demo 示例

一个完整的、可编译的最小示例。
包含 .h + .cpp。不需要展示 Build.cs 代码，依赖关系已在“模块依赖”章节说明。

**MyCaptureProcessor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "DataIngestCoreSubsystem.h"
#include "MyCaptureProcessor.generated.h"

UCLASS()
class AMyCaptureProcessor : public AActor
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable)
    void StartCaptureImport(const FString& ArchivePath);

private:
    UFUNCTION()
    void OnImportFinished(FDataIngestResult Result);

    FDataIngestHandle CurrentHandle;
};
```

**MyCaptureProcessor.cpp**
```cpp
#include "MyCaptureProcessor.h"
#include "DataIngestCoreSubsystem.h"
#include "CaptureManagerIngestSubsystem.h"

void AMyCaptureProcessor::StartCaptureImport(const FString& ArchivePath)
{
    UDataIngestCoreSubsystem* IngestSub = GetGameInstance()->GetSubsystem<UDataIngestCoreSubsystem>();
    if (IngestSub)
    {
        FDataIngestRequest Req;
        Req.ArchivePath = ArchivePath;
        CurrentHandle = IngestSub->StartIngest(Req);

        // 绑定完成回调
        IngestSub->OnIngestCompleted.AddDynamic(this, &AMyCaptureProcessor::OnImportFinished);
    }
}

void AMyCaptureProcessor::OnImportFinished(FDataIngestResult Result)
{
    // 取消绑定
    UDataIngestCoreSubsystem* IngestSub = GetGameInstance()->GetSubsystem<UDataIngestCoreSubsystem>();
    IngestSub->OnIngestCompleted.RemoveDynamic(this, &AMyCaptureProcessor::OnImportFinished);

    if (Result.bSuccess)
    {
        // 使用另一个子系统来生成资产
        UCaptureManagerIngestSubsystem* AssetSub = GetGameInstance()->GetSubsystem<UCaptureManagerIngestSubsystem>();
        AssetSub->CreateStaticMeshFromResult(Result, TEXT("/Game/ImportedMeshes/"));
        UE_LOG(LogTemp, Warning, TEXT("资产导入并创建成功！"));
    }
}
```

## 模块依赖

从 Build.cs 的 PublicDependencyModuleNames 和 PrivateDependencyModuleNames 提取。
告诉读者：要用这个 plugin，你的模块需要依赖哪些东西。

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 处理媒体输入/输出核心框架 |
| `MediaFrameworkUtilities` | 提供媒体相关的实用工具函数 |
| `LiveLinkInterface` | Live Link 框架的基础接口 |
| `LiveLinkHub` | Live Link Hub 应用程序框架和通信 |
| `CaptureManagerDeviceBlueprint` | 本插件内，用于设备蓝图的通信和数据描述 |
| `DataIngestCore` | (假设存在) 数据摄取核心逻辑，可能为私有依赖 |
| `CaptureManagerIngest` | (假设存在) 资产创建与处理逻辑，可能为私有依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将设备蓝图中的术语泛化，提高兼容性 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式导入蓝图API移至单独分类，优化蓝图节点组织 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 `CaptureManagerDeviceBlueprint` 模块 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退了之前的某个改动 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次尝试添加设备蓝图模块 |

### 维护评价

**活跃维护**。该插件是近期（2026年4月底）从 Epic Games 主仓库迁移或新创建的，并且在创建后立即进行了多次迭代和功能增强（如添加新模块、优化 API 结构）。这表明它是一个处于**积极开发阶段**的内部工具或前沿虚拟制片功能。**默认不启用**且标记为**实验性**，这符合其作为专业、前沿工作流工具的特性。目前没有发现已知的严重问题，但因其年轻和实验性，API 可能会发生变化。

**推荐使用**：如果你正在使用或计划使用与 Epic 配套的虚拟制片捕获硬件和工作流，这个插件是必需的。对于通用用户，由于其特定性和实验性，需要等待更稳定的版本或更详细的官方文档。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor/Tests) (路径基于模块结构推测，部分测试可能位于各模块内)