# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设备蓝图库） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

Capture Manager Editor 是虚幻引擎虚拟制作流程中的**采集数据导入与设备管理**插件。它解决的核心问题是：将运行 LiveLink Face 等应用的移动设备（iPhone/iPad）上录制的面部/身体动作捕获数据，自动化地下载、筛选并导入到 UE 或 UEFN 中，生成可直接使用的资产。

该插件提供了完整的设备通信链路：通过 IP 连接设备 → 获取录制列表（Takes）→ 按条件筛选 → 批量下载到本地 → 导入为引擎资产。这使得虚拟制片团队可以高效地管理大量捕获数据，而无需手动操作文件传输。

插件包含 7 个模块，覆盖设备蓝图通信、数据导入核心、LiveLink Hub 发现与导出等全链路能力。

## 使用场景

- 你在做虚拟制片项目，需要用 iPhone 上的 LiveLink Face 录制面部动画 → 用此插件自动下载和导入捕获数据
- 你需要批量管理设备上的大量 Takes，按日期、Slate 名称等条件筛选后批量下载 → 使用过滤和批量下载功能
- 你在构建 LiveLink Hub 工作流，需要发现和管理远程设备 → 使用 LiveLinkHubDiscovery 和 WorkerManager 模块
- 你在编写 Python 脚本自动化采集流程 → 使用 Blocking（同步）版本的蓝图/Python API

## 蓝图用法

所有设备相关蓝图节点位于 `CaptureManager|Device` 分类下，分为异步（带回调）和 Blocking（同步阻塞）两套 API。

### 设备连接与断开

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect to Device` | 通过 IP 连接设备，成功返回 Session 句柄 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Connect to Device (Blocking)` | 同步连接设备，阻塞直到成功或超时 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Disconnect Device` | 断开设备连接，释放 Session，取消所有进行中的下载 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Disconnect Device (Blocking)` | 同步断开设备连接 | `UCaptureManagerDeviceBlueprintLibrary` |

### Take 获取与下载

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Device Takes` | 获取设备上所有可用 Takes 的列表 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Get Device Takes (Blocking)` | 同步获取 Takes 列表 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Download Device Take` | 下载单个 Take 到本地目录 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Download Device Take (Blocking)` | 同步下载单个 Take | `UCaptureManagerDeviceBlueprintLibrary` |
| `Cancel Device Download` | 取消正在进行的单个 Take 下载 | `UCaptureManagerDeviceBlueprintLibrary` |

### 批量下载

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Download Device Takes (Batch)` | 顺序批量下载多个 Takes，每个 Take 独立回调 | `UCaptureManagerDeviceBatchDownloadLibrary` |
| `Download Device Takes (Batch Blocking)` | 同步批量下载，返回每个 Take 的结果数组 | `UCaptureManagerDeviceBatchDownloadLibrary` |
| `Cancel Batch Download` | 取消批量下载，当前 Take 失败并跳过剩余 | `UCaptureManagerDeviceBatchDownloadLibrary` |

### Take 过滤器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Filter Takes (Slate)` | 按 Slate 名称过滤，支持通配符 `*`，大小写不敏感 | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Filter Takes (Date Range)` | 按日期范围过滤，可只设置上界或下界 | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Get Latest Takes` | 获取最近 N 个 Takes（默认 1），按时间降序排列 | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Get Oldest Takes` | 获取最早 N 个 Takes，默认 1 | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Get Largest Takes` | 获取文件大小最大的 N 个 Takes | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Get Smallest Takes` | 获取文件大小最小的 N 个 Takes | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Get Latest Slate` | 获取最新 Slate 的所有 Takes（同一录制批次） | `UCaptureManagerDeviceTakeFiltersLibrary` |

### 使用示例（蓝图描述）

**示例 1：连接设备并下载最新 Take**

1. 拖入 `Connect to Device` 节点，填入设备 IP（端口默认 14785，超时 30 秒）
2. `OnSuccess` 引脚连接 `Get Device Takes`，传入返回的 Session
3. Takes 结果连接 `Get Latest Takes`（Count=1）获取最新一个
4. 再连接 `Download Device Take`，传入 Session、TakeName、本地目录路径
5. `OnSuccess` 引脚输出下载目录路径，可传给后续的 Ingest 节点

**示例 2：批量下载并过滤**

1. `Connect to Device` → `Get Device Takes` 获取全部 Takes
2. 连接 `Filter Takes (Slate)`，设置 SlatePattern 为 `"Slate01*"` 过滤特定批次
3. 连接 `Download Device Takes (Batch)`，传入过滤后的 Takes 数组和下载目录
4. `OnAllComplete` 引脚用于处理批量完成后的逻辑
5. 如需取消，调用 `Cancel Batch Download`

**示例 3：Python 脚本同步用法**

1. 使用 `Connect to Device (Blocking)` 获取 Session（同步，无需回调）
2. 使用 `Get Device Takes (Blocking)` 获取 Takes 列表
3. 使用 `Filter Takes (Date Range)` 设置日期范围筛选
4. 使用 `Download Device Take (Blocking)` 逐个同步下载

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManagerDeviceBlueprint/CaptureManagerDeviceBlueprintLibrary.h"
#include "CaptureManagerDeviceBlueprint/CaptureManagerDeviceBatchDownloadLibrary.h"
#include "CaptureManagerDeviceBlueprint/CaptureManagerDeviceTakeFiltersLibrary.h"
```

### 基本用法

异步连接设备并获取 Takes（来自 `CaptureManagerDeviceBlueprintLibrary.h`）：

```cpp
// 异步连接设备
UCaptureManagerDeviceBlueprintLibrary::ConnectToDevice(
    TEXT("My iPhone"),       // 设备显示名
    TEXT("192.168.1.100"),   // 设备 IP 地址
    14785,                   // 默认端口
    30,                      // 超时秒数
    FOnDeviceConnected::CreateLambda([this](UCaptureManagerDeviceSession* Session)
    {
        // 连接成功，获取 Takes 列表
        UCaptureManagerDeviceBlueprintLibrary::GetDeviceTakes(
            Session,
            FOnDeviceGetTakesResult::CreateLambda([Session](const TArray<FCaptureManagerDeviceTakeInfo>& Takes)
            {
                for (const auto& Take : Takes)
                {
                    UE_LOG(LogTemp, Log, TEXT("Take: %s, Slate: %s, Size: %lld bytes"),
                        *Take.TakeName, *Take.Slate, Take.TotalSizeBytes);
                }
            }),
            FOnDeviceGetTakesFailed::CreateLambda([](const FText& Error)
            {
                UE_LOG(LogTemp, Error, TEXT("Failed to get takes: %s"), *Error.ToString());
            })
        );
    }),
    FOnDeviceConnectFailed::CreateLambda([](const FText& Error)
    {
        UE_LOG(LogTemp, Error, TEXT("Connection failed: %s"), *Error.ToString());
    })
);
```

### 进阶用法

同步 API 适用于 Python 脚本或需要线性执行逻辑的场景（来自 `CaptureManagerDeviceBlueprintLibrary.h`）：

```cpp
// 同步连接设备（阻塞直到成功或超时）
ECaptureManagerDeviceError ErrorCode;
FText ErrorMessage;
UCaptureManagerDeviceSession* Session = UCaptureManagerDeviceBlueprintLibrary::ConnectToDeviceSync(
    TEXT("Studio iPad"),
    TEXT("192.168.1.100"),
    14785,
    30,
    ErrorCode,
    ErrorMessage
);

if (Session)
{
    // 同步获取 Takes
    TArray<FCaptureManagerDeviceTakeInfo> Takes = UCaptureManagerDeviceBlueprintLibrary::GetDeviceTakesSync(
        Session, ErrorCode, ErrorMessage);

    // 使用过滤器筛选最近的 Takes
    TArray<FCaptureManagerDeviceTakeInfo> LatestTakes =
        UCaptureManagerDeviceTakeFiltersLibrary::GetLatestTakes(Takes, 5);

    // 按日期范围过滤
    FDateTime OneWeekAgo = FDateTime::Now() - FTimespan::FromDays(7);
    TArray<FCaptureManagerDeviceTakeInfo> RecentTakes =
        UCaptureManagerDeviceTakeFiltersLibrary::FilterTakesByDateRange(
            Takes, OneWeekAgo, FDateTime());  // FDateTime() 表示不限上界

    // 批量下载（同步，阻塞直到全部完成）
    TArray<FCaptureManagerBatchDownloadResult> Results =
        UCaptureManagerDeviceBatchDownloadLibrary::DownloadDeviceTakesBatchSync(
            Session, RecentTakes, TEXT("/Game/Captures/"));

    for (const auto& Result : Results)
    {
        if (Result.bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Downloaded: %s -> %s"),
                *Result.TakeName, *Result.TakeDirectoryPath);
        }
    }

    // 同步断开
    UCaptureManagerDeviceBlueprintLibrary::DisconnectDeviceSync(Session);
}
```

错误处理使用 `ECaptureManagerDeviceError` 枚举（来自 `CaptureManagerDeviceSession.h`）：

```cpp
enum class ECaptureManagerDeviceError : uint8
{
    NoError,            // 无错误
    Unknown,            // 未知错误
    InvalidArgument,    // 参数无效
    ConnectionTimeout,  // 连接超时
    Disconnected,       // 设备断开
    TakeNotFound,       // Take 未找到
    DownloadFailed,     // 下载失败
    Canceled,           // 已取消
    ProtocolError,      // 协议错误
};
```

## Demo 示例

一个完整的最小示例：同步连接设备、获取最新 Takes 并下载。

```cpp
// MyCaptureManagerDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCaptureManagerDemo.generated.h"

UCLASS()
class AMyCaptureManagerDemo : public AActor
{
    GENERATED_BODY()

public:
    /** 触发一次完整的捕获数据下载流程 */
    UFUNCTION(BlueprintCallable)
    void DownloadLatestTake(const FString& DeviceIP, const FString& DownloadDir);
};
```

```cpp
// MyCaptureManagerDemo.cpp
#include "MyCaptureManagerDemo.h"
#include "CaptureManagerDeviceBlueprint/CaptureManagerDeviceBlueprintLibrary.h"
#include "CaptureManagerDeviceBlueprint/CaptureManagerDeviceBatchDownloadLibrary.h"
#include "CaptureManagerDeviceBlueprint/CaptureManagerDeviceTakeFiltersLibrary.h"

void AMyCaptureManagerDemo::DownloadLatestTake(const FString& DeviceIP, const FString& DownloadDir)
{
    ECaptureManagerDeviceError ErrorCode;
    FText ErrorMessage;

    // 1. 同步连接设备
    UCaptureManagerDeviceSession* Session =
        UCaptureManagerDeviceBlueprintLibrary::ConnectToDeviceSync(
            TEXT("Demo Device"), DeviceIP, 14785, 30, ErrorCode, ErrorMessage);

    if (!Session)
    {
        UE_LOG(LogTemp, Error, TEXT("连接失败: %s"), *ErrorMessage.ToString());
        return;
    }

    // 2. 获取所有 Takes
    TArray<FCaptureManagerDeviceTakeInfo> AllTakes =
        UCaptureManagerDeviceBlueprintLibrary::GetDeviceTakesSync(
            Session, ErrorCode, ErrorMessage);

    if (ErrorCode != ECaptureManagerDeviceError::NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("获取 Takes 失败: %s"), *ErrorMessage.ToString());
        UCaptureManagerDeviceBlueprintLibrary::DisconnectDeviceSync(Session);
        return;
    }

    // 3. 筛选最新的 3 个 Takes
    TArray<FCaptureManagerDeviceTakeInfo> LatestTakes =
        UCaptureManagerDeviceTakeFiltersLibrary::GetLatestTakes(AllTakes, 3);

    // 4. 批量同步下载
    TArray<FCaptureManagerBatchDownloadResult> Results =
        UCaptureManagerDeviceBatchDownloadLibrary::DownloadDeviceTakesBatchSync(
            Session, LatestTakes, DownloadDir);

    for (const auto& Result : Results)
    {
        UE_LOG(LogTemp, Log, TEXT("[%s] %s -> %s"),
            Result.bSuccess ? TEXT("成功") : TEXT("失败"),
            *Result.TakeName,
            Result.bSuccess ? *Result.TakeDirectoryPath : *Result.ErrorMessage.ToString());
    }

    // 5. 断开连接
    UCaptureManagerDeviceBlueprintLibrary::DisconnectDeviceSync(Session);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 框架集成 |
| `LiveLinkInterface` | LiveLink 接口定义 |
| `MediaUtils` | 媒体工具（捕获数据处理） |
| `MediaAssets` | 媒体资产类型 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 泛化设备蓝图中的设备术语，提高通用性 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将同步阻塞式 Ingest 蓝图 API 移至 Blocking 子分类 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 模块 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退之前的提交 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次添加 CaptureManagerDeviceBlueprint 模块（后被回退再重新提交） |

### 维护评价

该插件创建于 2025 年 2 月，约 1 年历史，属于**活跃维护**状态。

- **近期活动密集**：2026 年 4 月底有多次连续提交，设备蓝图模块在反复迭代优化（先添加、回退、再添加、再改进术语）
- **功能仍在完善中**：Blocking 子分类的分离、设备术语的泛化表明 API 设计仍在打磨阶段
- **注意**：该插件默认未启用（`EnabledByDefault=false`），需在项目设置中手动开启
- **推荐使用**：如果你的虚拟制片工作流涉及移动设备捕获数据导入，此插件是官方推荐的标准化工具链。但鉴于 API 仍在快速迭代，注意关注版本更新中的 Breaking Changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- 官方文档（暂无）