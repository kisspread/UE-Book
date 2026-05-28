# Target Device Services Scripting

> Set of blueprint functions that enables working with TargetDeviceServices module via scripting

| 属性 | 值 |
|---|---|
| 中文名 | 设备服务脚本库 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TargetDeviceServicesScripting` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting) | |

## 用途

这个插件解决了一个特定问题：允许通过蓝图脚本和 Python 脚本访问和查询 Unreal Engine 的 `TargetDeviceServices` 模块中存储的设备信息。`TargetDeviceServices` 模块本身管理着可用于构建部署和测试的目标设备（如主机、移动设备、其他开发机等）的连接状态和信息。在没有此插件之前，这些信息主要在编辑器 UI 或 C++ 代码中可用。此插件通过提供蓝图函数，使得在编辑器工具、自动化脚本或 Python 脚本中能够程序化地查询这些设备信息成为可能。

## 使用场景

- 你正在编写一个自定义的编辑器工具或自动化测试框架，需要程序化地检查哪些目标设备当前可用、它们的类型和连接状态。
- 你需要在持续集成/持续部署 (CI/CD) 管道中，通过 Python 脚本动态选择或验证部署目标。
- 你希望在蓝图中构建一个设备列表 UI，用于显示当前网络上的可用开发设备。

## 蓝图用法

插件通过 `UBlueprintFunctionLibrary` 暴露了一组核心的蓝图函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Device Snapshots` | 获取网络中所有可用设备的快照信息，并按设备类型分组。返回一个字典（TMap），键是设备类型字符串，值是包含该类型所有设备快照的数组。 | `UTargetDeviceServicesBPFunctionLibrary` |

### 数据结构

插件定义了两个核心结构体用于在蓝图间传递数据：

1.  **`FDeviceSnapshot`**: 存储单个设备的详细信息快照，包括：
    *   `Name` (FString): 设备名称。
    *   `HostName` (FString): 设备主机名。
    *   `DeviceType` (FString): 设备类型（如 “Windows”, “Android”）。
    *   `ModelId` (FString): 设备型号标识符。
    *   `DeviceConnectionType` (FString): 连接类型（如 “Network”, “USB”）。
    *   `DeviceId` (FString): 设备唯一标识符。
    *   `OperatingSystem` (FString): 操作系统名称。
    *   `IsConnected` (bool): 设备当前是否已连接。

2.  **`FDeviceSnapshots`**: 一个简单的容器结构体，包含一个 `TArray<FDeviceSnapshot>` 类型的 `Entries` 数组。它被用作 `TMap` 中的值类型，以便在蓝图中方便地存储按类型分组的设备列表。

### 使用示例（蓝图描述）

1.  调用 `Get Device Snapshots` 节点。
2.  将其返回的 `TMap<FString, FDeviceSnapshots>` 存储到一个变量中。
3.  使用 `Map` 的 `Keys` 函数获取所有设备类型列表（例如：`["Windows", "Android", "Linux"]`）。
4.  遍历设备类型键，使用 `Find` 或 `[]` 操作符获取对应类型的 `FDeviceSnapshots`。
5.  遍历 `FDeviceSnapshots.Entries` 数组，即可获取每一台设备的详细信息（名称、状态等）。

## C++ 用法

此插件主要提供蓝图函数库，其 C++ 接口通常不被最终用户直接调用。其核心是 `UBlueprintFunctionLibrary` 的静态函数。

### 头文件引入

如果确实需要在 C++ 中使用（例如编写扩展该功能的插件），可以引入：
```cpp
#include "TargetDeviceServicesBPFunctionLibrary.h"
```

### 基本用法

```cpp
// 获取设备快照
TMap<FString, FDeviceSnapshots> AllDeviceSnapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

// 遍历结果
for (const auto& Pair : AllDeviceSnapshots)
{
    const FString& DeviceType = Pair.Key;
    const FDeviceSnapshots& Devices = Pair.Value;
    
    UE_LOG(LogTemp, Log, TEXT("设备类型: %s, 数量: %d"), *DeviceType, Devices.Entries.Num());
    
    for (const FDeviceSnapshot& Device : Devices.Entries)
    {
        UE_LOG(LogTemp, Log, TEXT("  - 名称: %s, 主机: %s, 已连接: %s"), 
            *Device.Name, *Device.HostName, Device.IsConnected ? TEXT("是") : TEXT("否"));
    }
}
```
*（此示例根据插件功能和结构体定义编写）*

### 进阶用法

由于插件仅提供一个核心静态函数，进阶用法通常结合 `TargetDeviceServices` 模块的其他 C++ API 来实现更复杂的设备管理逻辑，但这超出了此脚本库插件的范围。

## Demo 示例

一个简单的控制台命令示例，用于列出所有设备信息。

**TargetDeviceServicesScriptingDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "TargetDeviceServicesBPFunctionLibrary.h" // 引入插件结构体

class FTargetDeviceServicesScriptingDemo
{
public:
    static void ListAllDevices();
};
```

**TargetDeviceServicesScriptingDemo.cpp**
```cpp
#include "TargetDeviceServicesScriptingDemo.h"

void FTargetDeviceServicesScriptingDemo::ListAllDevices()
{
    TMap<FString, FDeviceSnapshots> Snapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();
    
    for (const auto& TypePair : Snapshots)
    {
        UE_LOG(LogTemp, Display, TEXT("=== 设备类型: %s ==="), *TypePair.Key);
        for (const FDeviceSnapshot& Snap : TypePair.Value.Entries)
        {
            UE_LOG(LogTemp, Display, TEXT("名称: %s | 主机: %s | ID: %s | 连接: %s"),
                *Snap.Name,
                *Snap.HostName,
                *Snap.DeviceId,
                Snap.IsConnected ? TEXT("已连接") : TEXT("已断开"));
        }
    }
}

// 可以通过控制台命令调用
static FAutoConsoleCommand CmdListDevices(
    TEXT("Demo.ListTargetDevices"),
    TEXT("列出所有可用的目标设备信息"),
    FConsoleCommandDelegate::CreateStatic(&FTargetDeviceServicesScriptingDemo::ListAllDevices)
);
```

## 模块依赖

从插件的功能和 `.Build.cs` 推断，使用者需要依赖：

| 模块 | 用途 |
|---|---|
| `TargetDeviceServices` | 提供被此脚本库封装的底层设备服务和数据访问功能。 |

**注意**：此插件本身是一个 `Editor` 类型插件，因此其功能仅在编辑器环境中可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 批量更新同时标记为实验性和Beta版的插件描述文件，属于维护性清理。 |
| 2023-11-02 | `63c9fe1c` | TargetDeviceServices - Fix long names in intermediate file names. | 修复插件名称过长导致中间文件名问题。 |
| 2023-11-02 | `0858844c` | TargetDeviceServices - Add plugin to be able to work with information stored in the TargetDeviceServ | 初始提交，创建插件，实现蓝图查询设备信息的核心功能。 |

### 维护评价

此插件创建于 2023 年 11 月，至今约 2 年。它是一个实验性 (`IsExperimentalVersion=true`) 的编辑器插件，且默认未启用 (`EnabledByDefault=false`)。从 Git 历史看，自初始功能提交后，仅有两次后续提交：一次是修复构建问题，另一次是针对实验性插件标签的批量维护性更新。**没有观察到功能性的增强或扩展**。这表明该插件功能相对稳定但可能处于早期或低优先级阶段，目前主要用于内部或特定场景的脚本访问，尚未成为广泛使用或积极维护的组件。由于其是实验性的且更新不活跃，使用时需注意其稳定性和未来兼容性可能无法保证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting)
- 官方文档: 未提供
- 测试用例: 未在插件目录内发现标准测试文件