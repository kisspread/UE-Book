# Target Device Services Scripting

> Set of blueprint functions that enables working with TargetDeviceServices module via scripting

| 属性 | 值 |
|---|---|
| 中文名 | 目标设备服务脚本 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TargetDeviceServicesScripting` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting) | |

## 用途

该插件的核心目的是为 **蓝图** 和 **Python 脚本** 提供一个简单的接口，用以访问 `TargetDeviceServices` 模块中存储的网络设备信息。它解决了一个具体问题：开发者需要在不编写 C++ 代码的情况下，动态地查询和获取在编辑器中可见的远程目标设备（如手机、其他电脑）的详细信息。通过该插件，这些信息可以通过标准的蓝图节点获取，从而便于构建自动化测试、远程部署或设备管理流程。

## 使用场景

-   你正在开发一个跨平台游戏，需要在运行时或编辑器中动态查询局域网内可用于测试的 Android、iOS 或其他设备。
-   你在构建一个自动化测试工具链，其中某个蓝图需要知道当前有哪些可用的测试设备及其属性，以便智能地分配测试任务。
-   你正在制作一个远程部署工具，希望通过可视化脚本选择并获取特定设备的信息。

## 蓝图用法

该插件通过一个蓝图函数库 (`UTargetDeviceServicesBPFunctionLibrary`) 暴露所有功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDeviceSnapshots` | 获取网络中所有可用设备的快照信息，并按设备类型分组返回。 | `UTargetDeviceServicesBPFunctionLibrary` |

### 使用示例（蓝图描述）

1.  **获取设备列表**：在你的蓝图图表中，右键调用 `Get Device Snapshots` 节点。
2.  **遍历设备类型**：该节点返回一个 `TMap`，键 (`Key`) 是设备类型字符串（如 “Android”），值 (`Value`) 是 `FDeviceSnapshots` 结构体，其中包含一个 `FDeviceSnapshot` 数组 (`Entries`)。
3.  **访问设备信息**：从 `FDeviceSnapshots` 中获取 `Entries` 数组，然后遍历数组中的每个 `FDeviceSnapshot` 元素。
4.  **读取设备属性**：在 `FDeviceSnapshot` 上，你可以读取 `Name`, `HostName`, `DeviceType`, `ModelId`, `DeviceConnectionType`, `DeviceId`, `OperatingSystem`, `IsConnected` 等只读属性，用于你的业务逻辑判断。

## C++ 用法

### 头文件引入

```cpp
#include “TargetDeviceServicesBPFunctionLibrary.h”
```

### 基本用法

通过函数库静态方法获取设备信息。

```cpp
// 获取所有设备快照，按设备类型分组
TMap<FString, FDeviceSnapshots> AllDeviceSnapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

// 遍历每种设备类型
for (auto& Pair : AllDeviceSnapshots)
{
    const FString& DeviceType = Pair.Key;
    const FDeviceSnapshots& DeviceSnapshotsOfType = Pair.Value;

    UE_LOG(LogTemp, Log, TEXT(“设备类型: %s, 数量: %d”), *DeviceType, DeviceSnapshotsOfType.Entries.Num());

    // 遍历该类型下的每一个设备
    for (const FDeviceSnapshot& Snapshot : DeviceSnapshotsOfType.Entries)
    {
        UE_LOG(LogTemp, Log, TEXT(“  设备名: %s, 主机名: %s, 已连接: %s”),
            *Snapshot.Name,
            *Snapshot.HostName,
            Snapshot.IsConnected ? TEXT(“是”) : TEXT(“否”));
    }
}
```

### 进阶用法

结合 `IsConnected` 标志筛选已连接的设备，并获取其操作系统信息。

```cpp
TArray<FDeviceSnapshot> ConnectedAndroidDevices;

if (const FDeviceSnapshots* AndroidDevices = AllDeviceSnapshots.Find(TEXT(“Android”)))
{
    for (const FDeviceSnapshot& Snapshot : AndroidDevices->Entries)
    {
        if (Snapshot.IsConnected)
        {
            ConnectedAndroidDevices.Add(Snapshot);
            UE_LOG(LogTemp, Log, TEXT(“已连接的 Android 设备: %s (%s)”),
                *Snapshot.Name,
                *Snapshot.OperatingSystem);
        }
    }
}
```

## Demo 示例

一个最小的 Actor 类，用于在 BeginPlay 时打印所有已连接设备的信息。

```cpp
// MyDeviceInfoPrinter.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “TargetDeviceServicesBPFunctionLibrary.h” // 包含插件头文件
#include “MyDeviceInfoPrinter.generated.h”

UCLASS()
class AMyDeviceInfoPrinter : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};

// MyDeviceInfoPrinter.cpp
#include “MyDeviceInfoPrinter.h”

void AMyDeviceInfoPrinter::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取所有设备快照
    TMap<FString, FDeviceSnapshots> Snapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

    UE_LOG(LogTemp, Warning, TEXT(“===== 开始扫描目标设备 =====”));

    // 2. 遍历并打印信息
    for (auto& Pair : Snapshots)
    {
        for (const FDeviceSnapshot& Device : Pair.Value.Entries)
        {
            if (Device.IsConnected)
            {
                UE_LOG(LogTemp, Log, TEXT(“[已连接] 类型: %s, 名称: %s, 主机: %s, 系统: %s”),
                    *Pair.Key,
                    *Device.Name,
                    *Device.HostName,
                    *Device.OperatingSystem);
            }
        }
    }

    UE_LOG(LogTemp, Warning, TEXT(“===== 设备扫描完成 =====”));
}
```

## 模块依赖

从 `Build.cs` 分析，使用此插件需要在你的 `.Build.cs` 文件中添加以下依赖模块：

| 模块 | 用途 |
|---|---|
| `TargetDeviceServices` | 核心的目标设备服务模块，提供设备管理的基础功能。 |
| `TargetDeviceServicesMessaging` | 目标设备服务的通信模块，处理设备发现和信息交换。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in the JSON file have had the IsBetaVersion flag removed. | 批量清理实验性插件的描述文件，移除了同时标记为Beta的插件的Beta标记。 |
| 2023-11-02 | `63c9fe1c` | TargetDeviceServices - Fix long names in intermediate file names. | 修复了插件中间文件名称过长可能导致的构建问题。 |
| 2023-11-02 | `0858844c` | TargetDeviceServices - Add plugin to be able to work with information stored in the TargetDeviceServices module via blueprints and Python. | 插件初始创建，实现蓝图和Python访问TargetDeviceServices设备信息的核心功能。 |

### 维护评价

该插件自 2023 年 11 月创建以来，除了一次必要的全局性清理外，未有新的功能更新或bug修复提交。它处于**实验性**状态，且功能范围非常单一（仅提供一个核心函数）。这表明它可能是一个功能性原型或内部工具，由 Epic 的特定团队（如构建系统或测试自动化团队）用于满足特定需求。对于普通开发者而言，**除非你明确需要在蓝图中查询 `TargetDeviceServices` 的底层设备信息，否则不建议主动启用**。它的存在更偏向于为 Epic 自身的工具链服务，社区支持和使用文档可能非常有限。考虑到其实验性和低活跃度，使用时需自行承担未来可能被移除的风险。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting)
-   (无官方文档链接)
-   (插件本身不包含测试用例)