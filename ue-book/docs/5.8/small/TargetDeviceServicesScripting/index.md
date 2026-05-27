# Target Device Services Scripting Library

> Set of blueprint functions that enables working with TargetDeviceServices module via scripting

| 属性 | 值 |
|---|---|
| 中文名 | 目标设备服务脚本库 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TargetDeviceServicesScripting` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-11-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting) | |

## 用途

该插件为 UE5 的 `TargetDeviceServices` 模块提供了一个蓝图和 Python 可用的脚本接口。`TargetDeviceServices` 模块通常用于管理连接到编辑器网络（如本地局域网）中的目标设备（例如，用于测试或部署的移动设备、游戏主机等）。此插件的核心作用是**将这些内部的设备信息和状态暴露给蓝图和 Python 脚本**，从而允许用户自动化地查询和获取可用的测试设备列表及其属性，例如设备名称、主机名、操作系统、连接状态等。

## 使用场景

- **多设备测试自动化**：当你需要在蓝图或 Python 脚本中动态获取网络上所有可用设备的列表，并根据设备类型或状态（如是否连接）来自动化测试部署流程。
- **设备管理仪表盘**：在编辑器工具或自定义编辑器模块中，通过脚本获取并显示当前连接的设备信息。
- **CI/CD 集成**：在持续集成和部署的脚本中，查询目标设备信息，用于判断构建应部署到哪些设备上进行验证。

## 蓝图用法

该插件主要暴露了一个静态蓝图函数，用于获取所有设备的信息快照。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetDeviceSnapshots` | 获取网络中所有可用设备的信息快照，并按设备类型分组返回。 | `UTargetDeviceServicesBPFunctionLibrary` |

### 数据结构

| 结构体 | 说明 |
|---|---|
| `FDeviceSnapshot` | 存储单个设备的详细信息快照，包括名称、主机名、设备类型、操作系统、是否连接等。 |
| `FDeviceSnapshots` | `FDeviceSnapshot` 的容器，用于在蓝图中表示一组设备（因为蓝图 TMap 的值类型需要是 UStruct）。 |

### 使用示例（蓝图描述）

1.  在任意蓝图图表中，右键搜索 “Get Device Snapshots” 节点并添加。
2.  该节点的输出引脚 `ReturnValue` 是一个 `TMap<String, FDeviceSnapshots>`。在蓝图中，这通常表现为一个键值对数组。
3.  你可以使用 “For Each Loop” 来迭代这个 Map。外层循环的 Key 是设备类型字符串（例如 “Android”， “IOS”），Value 是一个 `FDeviceSnapshots` 结构。
4.  对内层的 `FDeviceSnapshots.Entries` 数组再使用 “For Each Loop”，即可遍历每种类型下的所有设备。
5.  在内层循环中，你可以访问 `FDeviceSnapshot` 的各个属性（如 `Name`， `IsConnected` 等）来进行你的业务逻辑判断。

## C++ 用法

### 头文件引入

```cpp
#include "TargetDeviceServicesBPFunctionLibrary.h"
```

### 基本用法

从头文件可以直接调用静态函数获取设备信息。

```cpp
// 获取所有设备的快照信息，按设备类型分组
TMap<FString, FDeviceSnapshots> AllDeviceSnapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

// 遍历不同类型设备
for (const auto& Pair : AllDeviceSnapshots)
{
    const FString& DeviceType = Pair.Key;
    const FDeviceSnapshots& SnapshotsForType = Pair.Value;
    
    UE_LOG(LogTemp, Log, TEXT("Device Type: %s, Count: %d"), *DeviceType, SnapshotsForType.Entries.Num());

    // 遍历该类型下的所有设备
    for (const FDeviceSnapshot& Snapshot : SnapshotsForType.Entries)
    {
        UE_LOG(LogTemp, Log, TEXT("  - Device: %s (%s), Connected: %s"),
            *Snapshot.Name,
            *Snapshot.HostName,
            Snapshot.IsConnected ? TEXT("Yes") : TEXT("No"));
    }
}
```
*（来源：基于 `Public/TargetDeviceServicesBPFunctionLibrary.h` 文件中的 API 定义）*

## Demo 示例

以下是一个在自定义编辑器工具中使用该插件功能的最小 C++ 示例。

**MyEditorTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyEditorTool
{
public:
    static void ListAvailableDevices();
};
```

**MyEditorTool.cpp**
```cpp
#include "MyEditorTool.h"
#include "TargetDeviceServicesBPFunctionLibrary.h"
#include "Misc/MessageDialog.h"

void FMyEditorTool::ListAvailableDevices()
{
    // 获取设备快照
    TMap<FString, FDeviceSnapshots> Snapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();
    
    FString LogOutput = TEXT("Available Devices:\n");
    
    for (const auto& Pair : Snapshots)
    {
        for (const FDeviceSnapshot& Snapshot : Pair.Value.Entries)
        {
            LogOutput += FString::Printf(TEXT("  [%s] %s (%s) - %s\n"),
                *Pair.Key,
                *Snapshot.Name,
                *Snapshot.HostName,
                Snapshot.IsConnected ? TEXT("Connected") : TEXT("Disconnected"));
        }
    }
    
    // 在编辑器中显示一个包含设备列表的对话框
    FMessageDialog::Open(EAppMsgType::Ok, FText::FromString(LogOutput));
}
```

## 模块依赖

根据插件的功能和常见的 `TargetDeviceServices` 模块结构，使用者的模块可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `TargetDeviceServices` | 提供核心的设备管理和通信功能，是此脚本库的数据来源。 |
| `DeviceManagerServices` | 可能用于更底层的设备管理协议和会话。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 批量更新了同时标记为实验性和Beta的.uplugin描述文件，属于元数据维护。 |
| 2023-11-02 | `63c9fe1c` | TargetDeviceServices - Fix long names in intermediate file names. | 修复了中间文件名过长的问题，属于构建稳定性修复。 |
| 2023-11-02 | `0858844c` | TargetDeviceServices - Add plugin to be able to work with information stored in the TargetDeviceServices module via blueprints and Python. | 插件初始提交，实现了通过蓝图和Python访问TargetDeviceServices信息的核心功能。 |

### 维护评价

- **创建时间**：2023年11月，插件较为年轻。
- **最近更新**：最后一次实质性功能提交在2023年11月。2024年11月的更新仅为插件描述元数据的批量维护，不涉及插件本身功能。
- **活跃度**：自创建以来，近一年内没有功能更新或Bug修复，**维护不活跃**。
- **已知问题**：作为实验性插件，其API和功能可能在未来版本中发生变更或被移除。
- **推荐使用**：由于其**实验性**状态和较低的维护频率，建议仅在需要该特定脚本化访问功能，且了解其潜在不稳定性风险的项目中使用。不推荐用于生产环境的核心功能。

**警告**：该插件已超过一年没有实质性功能更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting/Tests) （如果存在）