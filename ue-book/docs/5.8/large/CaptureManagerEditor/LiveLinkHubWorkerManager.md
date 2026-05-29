# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、内容数据） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

该插件是 Unreal Engine 虚拟制片（Virtual Production）流水线中的一个核心工具，主要功能是将来自外部设备（如 iPhone 的 TrueDepth 摄像头或其他专业动捕设备）捕获的表演数据（如面部动画、身体动作、音频等）打包成的“存档”（Archive）数据，自动导入到引擎中，并创建对应的资产（如动画序列、媒体纹理、音频波形等），以供后续的动画、合成或实时渲染使用。它通过一个中央“工作者管理器”（Worker Manager）来协调多个设备的连接、数据接收和导入任务。

## 使用场景

- 你正在制作一个需要高保真面部或身体动画的虚拟人项目，使用了专业的动捕设备或 iPhone 进行录制。
- 你的虚拟制片流水线需要一个自动化工具，将设备录制的原始数据快速、可靠地转化为 UE 可用的动画和媒体资产。
- 你需要在项目中管理多个捕获设备，并跟踪它们的导入任务状态。

## 蓝图用法

该插件的主要功能通过 C++ 类提供，公开的蓝图 API 有限，主要用于获取管理器状态和触发操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `获取管理器` | 获取 Live Link Hub 工作管理器的单例引用。 | `ULiveLinkHubWorkerManagerLibrary` |

### 使用示例（蓝图描述）

在蓝图中，你可以通过 `ULiveLinkHubWorkerManagerLibrary` 的静态函数获取 `FLiveLinkHubWorkerManager` 的实例。该管理器主要用于检查连接状态，但数据接收和导入的核心流程是后台自动处理的，通常不需要蓝图直接调用。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkHubWorkerManagerModule.h"
#include "LiveLinkHubWorkerManager.h"
```

### 基本用法

获取工作者管理器并检查连接状态。
```cpp
// 获取模块实例
FLiveLinkHubWorkerManagerModule& Module = FModuleManager::Get().GetModuleChecked<FLiveLinkHubWorkerManagerModule>(TEXT("LiveLinkHubWorkerManager"));

// 获取管理器实例
TSharedRef<FLiveLinkHubWorkerManager> WorkerManager = Module.GetManager();

// 检查是否有设备连接
if (WorkerManager->IsConnected())
{
    UE_LOG(LogTemp, Log, TEXT("有捕获设备已连接。"));
}
```
*来源：根据 `FLiveLinkHubWorkerManagerModule` 和 `FLiveLinkHubWorkerManager` 的公共接口推断。*

### 进阶用法

断开所有连接并响应设备发现请求。
```cpp
// 主动断开所有设备
WorkerManager->Disconnect();

// 构造并发送一个发现响应（例如，当引擎收到设备的广播时）
FDiscoveryResponse* Response = new FDiscoveryResponse(/* 填充必要数据 */);
FMessageAddress DeviceAddress; // 从网络消息中获得的设备地址
WorkerManager->SendDiscoveryResponse(Response, DeviceAddress);
```
*来源：根据 `FLiveLinkHubWorkerManager` 的公共方法 `Disconnect` 和 `SendDiscoveryResponse` 推断。*

## Demo 示例

一个展示如何初始化并获取工作者管理器的最小 Actor 类。
**CaptureManagerDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CaptureManagerDemoActor.generated.h"

class FLiveLinkHubWorkerManager;

UCLASS()
class ACaptureManagerDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ACaptureManagerDemoActor();

    virtual void BeginPlay() override;

private:
    TSharedPtr<FLiveLinkHubWorkerManager> WorkerManager;
};
```
**CaptureManagerDemoActor.cpp**
```cpp
#include "CaptureManagerDemoActor.h"
#include "LiveLinkHubWorkerManagerModule.h"

ACaptureManagerDemoActor::ACaptureManagerDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ACaptureManagerDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 确保模块已加载
    if (FModuleManager::Get().IsModuleLoaded(TEXT("LiveLinkHubWorkerManager")))
    {
        FLiveLinkHubWorkerManagerModule& Module = FModuleManager::Get().GetModuleChecked<FLiveLinkHubWorkerManagerModule>(TEXT("LiveLinkHubWorkerManager"));
        WorkerManager = Module.GetManager();

        if (WorkerManager.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("成功获取 LiveLink Hub 工作管理器，当前连接状态：%s"),
                WorkerManager->IsConnected() ? TEXT("已连接") : TEXT("未连接"));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("LiveLinkHubWorkerManager 模块未加载。"));
    }
}
```

## 模块依赖

该插件的模块主要作为虚拟制片生态系统的内部组件，其依赖关系旨在处理网络通信和数据摄入。对于使用者而言，通常无需直接在你的 `Build.cs` 中添加这些依赖，除非你正在开发扩展现有工作流的定制模块。

| 模块 | 用途 |
|---|---|
| `LiveLinkHub` | Live Link Hub 的核心模块，用于设备发现和连接管理。 |
| `CaptureManager` | 捕获数据管理的核心逻辑，负责数据处理和资产创建。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将设备蓝图中的特定术语通用化，提高代码兼容性。 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式的摄入蓝图 API 移至“Blocking”子分类，改善蓝图节点组织。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增设备蓝图模块，扩展设备集成能力。 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退了之前的某次更改（CL53274396）。 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次添加设备蓝图模块（后被回退）。 |

### 维护评价

该插件自 2025 年 2 月创建以来，处于**活跃开发**阶段。从最近的提交记录（2026 年 4 月底）可以看出，Epic Games 团队正在持续为其添加新功能（如设备蓝图模块）并进行优化（如重构代码结构、改善蓝图 API 组织）。虽然插件默认未启用，但其密集的更新表明它在虚拟制片管线中是一个重要且正在演进的工具。

**推荐使用**：如果你的项目涉及从外部设备导入动捕数据，这是一个官方提供的、正在积极维护的专业工具，可以显著提升工作流效率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- 官方文档（无）
- 测试用例（无公开路径）