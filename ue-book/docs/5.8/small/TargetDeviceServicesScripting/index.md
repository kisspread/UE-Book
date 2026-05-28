# TargetDeviceServices Scripting Library

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

TargetDeviceServices 模块负责管理网络中可用的远程目标设备（如其他电脑、主机等），但其 API 仅对 C++ 可用。本插件作为一层薄封装，将 TargetDeviceServices 中的设备信息以蓝图节点和 Python 脚本的形式暴露出来，使得设计师和技术美术无需编写 C++ 代码即可查询网络中已连接设备的快照信息（设备名、主机名、类型、操作系统等）。

**为什么存在？** UE 的设备管理流程（部署、远程运行等）依赖 TargetDeviceServices 模块，但此前只能通过 C++ 或编辑器 UI 访问。本插件填补了蓝图/Python 脚本化的空白，适合在自动化流水线或编辑器工具脚本中批量查询设备状态。

## 使用场景

- 你需要在编辑器工具脚本或 Python 自动化流程中查询当前网络中可用的目标设备列表
- 你需要根据设备类型（PC、主机等）分组获取设备信息，用于自定义部署策略
- 你想在蓝图中实现一个"选择目标设备"的 UI，展示已连接设备的详细信息

## 蓝图用法

本插件仅暴露一个蓝图函数节点，加上两个数据结构体。

### 核心结构体

| 结构体 | 说明 |
|---|---|
| `FDeviceSnapshot` | 单个设备的信息快照，包含 Name、HostName、DeviceType、ModelId、DeviceConnectionType、DeviceId、OperatingSystem、IsConnected |
| `FDeviceSnapshots` | 设备快照数组的容器，内部持有 `TArray<FDeviceSnapshot> Entries`，用于作为 TMap 的值类型 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Device Snapshots` | 获取网络中所有可用设备的快照，按设备类型分组返回字典 | `UTargetDeviceServicesBPFunctionLibrary` |

### 使用示例（蓝图描述）

1. 在任意蓝图的事件图表中，添加 **Get Device Snapshots** 节点
2. 返回值类型为 `TMap<FString, FDeviceSnapshots>`，键为设备类型字符串（如 `"Windows"`、`"IOS"` 等），值为该类型下的所有设备快照数组
3. 使用 **For Each Loop** 遍历字典，对每个键值对：
   - 键（FString）即设备类型
   - 值（FDeviceSnapshots）的 `Entries` 数组可通过 **Get** 节点逐个访问每个 `FDeviceSnapshot`
4. 从 `FDeviceSnapshot` 中读取所需字段：`Name`（设备名）、`HostName`（主机名）、`IsConnected`（是否已连接）等

## C++ 用法

由于本插件仅有一个函数，且主要面向蓝图/Python，C++ 用法较为简单。

### 头文件引入

```cpp
#include "TargetDeviceServicesBPFunctionLibrary.h"
```

### 基本用法

直接调用静态函数获取设备快照：

```cpp
// 获取网络中所有设备的快照，按设备类型分组
TMap<FString, FDeviceSnapshots> DeviceSnapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

// 遍历每种设备类型
for (const auto& Pair : DeviceSnapshots)
{
    const FString& DeviceType = Pair.Key;
    const FDeviceSnapshots& Snapshots = Pair.Value;
    
    UE_LOG(LogTemp, Log, TEXT("Device Type: %s, Count: %d"), *DeviceType, Snapshots.Entries.Num());
    
    // 遍历该类型下的每个设备
    for (const FDeviceSnapshot& Snapshot : Snapshots.Entries)
    {
        UE_LOG(LogTemp, Log, TEXT("  Device: %s | Host: %s | Connected: %s"),
            *Snapshot.Name,
            *Snapshot.HostName,
            Snapshot.IsConnected ? TEXT("Yes") : TEXT("No"));
    }
}
```

### 进阶用法

过滤出特定类型或已连接的设备：

```cpp
TMap<FString, FDeviceSnapshots> AllDevices = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

// 收集所有已连接的 Windows 设备
TArray<FDeviceSnapshot> ConnectedWindowsDevices;
if (const FDeviceSnapshots* WindowsGroup = AllDevices.Find(TEXT("Windows")))
{
    for (const FDeviceSnapshot& Device : WindowsGroup->Entries)
    {
        if (Device.IsConnected)
        {
            ConnectedWindowsDevices.Add(Device);
        }
    }
}

UE_LOG(LogTemp, Log, TEXT("Connected Windows devices: %d"), ConnectedWindowsDevices.Num());
```

## Demo 示例

一个最小的编辑器工具模块，查询设备并打印结果。

### DeviceQueryDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FDeviceQueryDemo
{
public:
    /** 打印当前网络中所有已连接设备的信息 */
    static void PrintConnectedDevices();
};
```

### DeviceQueryDemo.cpp

```cpp
#include "DeviceQueryDemo.h"
#include "TargetDeviceServicesBPFunctionLibrary.h"

void FDeviceQueryDemo::PrintConnectedDevices()
{
    const TMap<FString, FDeviceSnapshots> Snapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

    int32 TotalDevices = 0;
    int32 ConnectedDevices = 0;

    for (const auto& Pair : Snapshots)
    {
        for (const FDeviceSnapshot& Device : Pair.Value.Entries)
        {
            TotalDevices++;
            if (Device.IsConnected)
            {
                ConnectedDevices++;
                UE_LOG(LogTemp, Display, TEXT("[Connected] %s (%s) - %s | OS: %s"),
                    *Device.Name, *Pair.Key, *Device.HostName, *Device.OperatingSystem);
            }
        }
    }

    UE_LOG(LogTemp, Display, TEXT("Total: %d devices, Connected: %d"), TotalDevices, ConnectedDevices);
}
```

## 模块依赖

由于 Build.cs 内容未提供，以下基于源码推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `TargetDeviceServices` | 核心依赖，本插件封装的底层设备管理模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th... | 批量更新实验性/Beta 标记的 uplugin 元数据，非功能性改动 |
| 2023-11-02 | `63c9fe1c` | TargetDeviceServices - Fix long names in intermediate file names. | 修复中间文件名过长的构建问题 |
| 2023-11-02 | `0858844c` | TargetDeviceServices - Add plugin to be able to work with information stored in the TargetDeviceServices module via blueprints and Python. | 插件初始创建，暴露设备服务信息至蓝图和 Python |

### 维护评价

⚠️ **本插件自 2023 年 11 月创建以来，从未有过功能性更新。** 仅有一次 2024 年 11 月的批量元数据调整（不涉及任何代码变更）。

- **创建时间**：2023-11-02，仅约 2 年历史
- **功能极简**：整个插件只有 1 个函数、2 个结构体，功能单一且完整
- **实验性状态**：标记为 Experimental 且默认未启用，表明 Epic 尚未承诺长期维护
- **API 稳定性**：由于功能极简，不太可能有破坏性变更，但也意味着可能被合并到主模块或废弃
- **推荐程度**：如果你的项目需要通过蓝图/Python 查询目标设备信息，可以使用，但需注意这是实验性功能。在正式项目中建议关注 Epic 的后续动向，必要时自行封装 TargetDeviceServices 模块

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting)
- 官方文档：无