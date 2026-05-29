# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、工具UI） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

Capture Manager Editor 是一个用于虚拟制作流程的插件套件。其核心功能是**管理从移动设备（如运行LiveLink Face应用的iPhone/iPad）捕获的面部表演数据**。它提供了一套完整的工具链，用于：
1.  **设备发现与连接**：通过IP地址与运行LiveLink Face的设备建立连接。
2.  **数据获取与管理**：从已连接的设备上列出、过滤和查看可用的“Take”（一次完整的录制）。
3.  **数据下载**：将设备上的Take文件批量或单个下载到本地磁盘。
4.  **资产导入**：将下载的Take数据导入到UE项目中，创建必要的资产（如动画、序列等）。

它解决了虚拟制作中**高效、自动化地从移动设备采集和管理面部捕捉数据**的问题，是连接移动捕获端与UE内容创作端的关键桥梁。

## 使用场景

- **虚拟制片现场**：在拍摄现场，通过iPad上的LiveLink Face应用录制演员的面部表演，然后使用此插件将数据批量导入到UE中进行预览或后期处理。
- **自动化数据采集流水线**：编写Python脚本或蓝图，定期连接到指定设备，自动下载最新的Take，实现无人值守的数据采集。
- **多设备管理**：同时管理多个连接的移动设备，分别下载它们的捕获数据。

## 蓝图用法

主要蓝图功能封装在 `UCaptureManagerDeviceBlueprintLibrary`、`UCaptureManagerDeviceBatchDownloadLibrary` 和 `UCaptureManagerDeviceTakeFiltersLibrary` 中。

### 核心节点

#### 设备连接与操作 (`UCaptureManagerDeviceBlueprintLibrary`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Connect to Device` | 通过IP和端口异步连接到设备，返回会话句柄。 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Connect to Device (Blocking)` | 同步阻塞版本的连接，适用于Python脚本。 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Get Device Takes` | 异步获取设备上的所有Take列表。 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Download Device Take` | 异步下载指定Take到本地目录。 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Disconnect Device` | 异步断开设备连接并释放会话。 | `UCaptureManagerDeviceBlueprintLibrary` |
| `Cancel Device Download` | 取消正在进行的Take下载。 | `UCaptureManagerDeviceBlueprintLibrary` |

#### 批量下载 (`UCaptureManagerDeviceBatchDownloadLibrary`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Download Device Takes (Batch)` | 异步顺序下载多个Take。 | `UCaptureManagerDeviceBatchDownloadLibrary` |
| `Cancel Batch Download` | 取消整个批量下载任务。 | `UCaptureManagerDeviceBatchDownloadLibrary` |

#### Take过滤 (`UCaptureManagerDeviceTakeFiltersLibrary`)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Filter Takes (Slate)` | 按场景名（Slate）模式过滤Take列表，支持通配符。 | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Filter Takes (Date Range)` | 按日期范围过滤Take列表。 | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Get Latest Takes` | 获取最近N个Take。 | `UCaptureManagerDeviceTakeFiltersLibrary` |
| `Get Latest Slate` | 获取最新场景的所有Take。 | `UCaptureManagerDeviceTakeFiltersLibrary` |

### 使用示例（蓝图描述）
一个典型的蓝图工作流：
1.  使用 `Connect to Device` 节点，输入设备的IP地址（默认端口14785），获取 `UCaptureManagerDeviceSession` 对象。
2.  将会话对象传给 `Get Device Takes` 节点，获取 `FCaptureManagerDeviceTakeInfo` 数组。
3.  （可选）使用 `Filter Takes (Slate)` 节点过滤出特定场景的Take。
4.  将会话对象和过滤后的Take数组传给 `Download Device Takes (Batch)` 节点，指定本地下载根目录。
5.  通过 `OnTakeSuccess` 等委托监听每个Take的下载进度和结果。
6.  所有操作完成后，使用 `Disconnect Device` 断开连接。

## C++ 用法

### 头文件引入
```cpp
#include "CaptureManagerDeviceBlueprintLibrary.h"
#include "CaptureManagerDeviceSession.h"
```

### 基本用法
核心操作都围绕 `UCaptureManagerDeviceSession` 对象进行。
```cpp
// 来自 CaptureManagerDeviceBlueprintLibrary.h 注释和测试用例模式
// 1. 创建会话并连接
UCaptureManagerDeviceSession* Session = NewObject<UCaptureManagerDeviceSession>();
ECaptureManagerDeviceError ErrorCode;
FText ErrorMessage;
bool bConnected = Session->Connect(TEXT("192.168.1.100"), 14785, 30.0f, ErrorCode, ErrorMessage);

if (bConnected)
{
    // 2. 获取Take列表
    TArray<FCaptureManagerDeviceTakeInfo> Takes;
    Session->FetchTakes(Takes, ErrorCode, ErrorMessage);
    
    // 3. 下载单个Take
    FString DownloadDir = FPaths::ProjectSavedDir() / TEXT("Captures");
    FString TakeDirPath;
    Session->DownloadTake(Takes[0].TakeName, DownloadDir, TakeDirPath, ErrorCode, ErrorMessage);
    
    // 4. 断开连接
    Session->Disconnect();
}
```

### 进阶用法
使用蓝图库的同步版本，方便编写脚本。
```cpp
// 来自 CaptureManagerDeviceBlueprintLibrary.h 的注释
// 同步连接
ECaptureManagerDeviceError ErrorCode;
FText ErrorMessage;
UCaptureManagerDeviceSession* Session = UCaptureManagerDeviceBlueprintLibrary::ConnectToDeviceSync(
    TEXT("MyPhone"), TEXT("192.168.1.100"), 14785, 30.0f, ErrorCode, ErrorMessage);

if (Session)
{
    // 同步获取Take
    TArray<FCaptureManagerDeviceTakeInfo> Takes = UCaptureManagerDeviceBlueprintLibrary::GetDeviceTakesSync(Session, ErrorCode, ErrorMessage);
    
    // 同步批量下载
    TArray<FCaptureManagerBatchDownloadResult> Results = UCaptureManagerDeviceBatchDownloadLibrary::DownloadDeviceTakesBatchSync(
        Session, Takes, DownloadDir);
    
    // 处理结果
    for (const auto& Result : Results)
    {
        UE_LOG(LogTemp, Log, TEXT("Take %s: %s"), *Result.TakeName, Result.bSuccess ? TEXT("Success") : TEXT("Failed"));
    }
    
    // 同步断开
    UCaptureManagerDeviceBlueprintLibrary::DisconnectDeviceSync(Session);
}
```

## Demo 示例

一个简单的命令行工具，连接设备并下载最新的Take。
```cpp
// CaptureManagerDemo.h
#pragma once
#include "CoreMinimal.h"

class FCaptureManagerDemo
{
public:
    static void Run();
};
```
```cpp
// CaptureManagerDemo.cpp
#include "CaptureManagerDemo.h"
#include "CaptureManagerDeviceBlueprintLibrary.h"
#include "CaptureManagerDeviceTakeFiltersLibrary.h"

void FCaptureManagerDemo::Run()
{
    // 阻塞连接
    ECaptureManagerDeviceError ErrorCode;
    FText ErrorMessage;
    UCaptureManagerDeviceSession* Session = UCaptureManagerDeviceBlueprintLibrary::ConnectToDeviceSync(
        TEXT("DemoDevice"), TEXT("192.168.1.55"), 14785, 10.0f, ErrorCode, ErrorMessage);
    
    if (!Session || ErrorCode != ECaptureManagerDeviceError::NoError)
    {
        UE_LOG(LogTemp, Error, TEXT("连接失败: %s"), *ErrorMessage.ToString());
        return;
    }
    
    // 获取并过滤最新的一个Take
    TArray<FCaptureManagerDeviceTakeInfo> AllTakes = UCaptureManagerDeviceBlueprintLibrary::GetDeviceTakesSync(Session, ErrorCode, ErrorMessage);
    TArray<FCaptureManagerDeviceTakeInfo> LatestTakes = UCaptureManagerDeviceTakeFiltersLibrary::GetLatestTakes(AllTakes, 1);
    
    if (LatestTakes.Num() > 0)
    {
        // 下载
        FString DownloadPath = FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir() / TEXT("DemoCaptures"));
        ECaptureManagerDeviceError DownloadError;
        FText DownloadErrorMsg;
        FString ResultPath = UCaptureManagerDeviceBlueprintLibrary::DownloadDeviceTakeSync(
            Session, LatestTakes[0].TakeName, DownloadPath, DownloadError, DownloadErrorMsg);
        
        if (!ResultPath.IsEmpty())
        {
            UE_LOG(LogTemp, Log, TEXT("下载成功，路径: %s"), *ResultPath);
        }
    }
    
    // 清理
    UCaptureManagerDeviceBlueprintLibrary::DisconnectDeviceSync(Session);
}
```

## 模块依赖

根据插件名称和功能推断，`CaptureManagerDeviceBlueprint` 模块可能依赖以下独特模块：
*注意：以下为基于功能的推断，实际依赖需查阅 `CaptureManagerDeviceBlueprint.Build.cs` 文件。*

| 模块 | 用途 |
|---|---|
| `LiveLink` | 处理与LiveLink Face应用的通信协议 |
| `Json` | 解析设备返回的Take元数据（JSON格式） |
| `HTTP` | 用于可能的设备发现或数据传输（待确认） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将设备蓝图中的“iPhone/iPad”等具体术语泛化为“设备” |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式导入API移至“Blocking”子分类，优化蓝图节点组织 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 添加了CaptureManagerDeviceBlueprint模块 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回滚了某个变更 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 初次添加CaptureManagerDeviceBlueprint模块 |

### 维护评价
- **创建时间**：非常新的插件（2025年2月创建）。
- **近期活跃度**：**非常活跃**。在文档生成的基期（2025年）前后（2026年4月底）有多次密集的提交，主要是添加核心模块和优化API设计。
- **功能状态**：插件仍在积极开发中，属于较新的虚拟制作工具链。
- **推荐度**：**强烈推荐**。这是Epic官方为虚拟制作提供的最新设备管理工具，API设计现代（同时提供异步和同步版本），且处于快速迭代期，适合作为新项目的首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [官方文档]() (暂无)
- [测试用例]() (暂未在源码中发现独立的自动化测试文件)