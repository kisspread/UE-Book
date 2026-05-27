# Target Device Services Scripting Library

> Set of blueprint functions that enables working with TargetDeviceServices module via scripting

| 属性 | 值 |
|---|---|
| 中文名 | 设备服务蓝图脚本库 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TargetDeviceServicesScripting` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting) | |

## 用途

这个插件为 **TargetDeviceServices** 模块提供了蓝图和 Python 可调用的脚本接口。TargetDeviceServices 模块本身管理着局域网内可用的目标设备信息（如设备名称、主机名、类型、操作系统、连接状态等），但它主要是一个 C++/编辑器内部模块，没有直接暴露给蓝图。

此插件的核心价值是**架桥**：将 TargetDeviceServices 内部存储的设备信息快照导出为蓝图可用的结构体和函数。使用场景包括：在编辑器工具蓝图中查询可用的部署/测试设备、按设备类型分组显示设备列表、检查设备连接状态等。

这是一个非常轻量的桥接插件（仅 3 个源文件），功能单一且聚焦。

## 使用场景

- 你在编写编辑器工具蓝图，需要查询当前局域网中可用的目标设备 → 用此插件获取设备快照
- 你需要通过 Python 脚本自动化获取设备列表（用于 CI/CD 或测试流水线） → 用此插件提供的脚本接口
- 你需要按设备类型（如 Windows、Mac、主机等）分组查看设备信息 → `GetDeviceSnapshots()` 返回按设备类型分组的 Map

## 蓝图用法

插件仅暴露一个蓝图函数，搭配两个数据结构体使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Device Snapshots` | 获取网络中所有可用设备的快照信息，按设备类型分组返回 | `UTargetDeviceServicesBPFunctionLibrary` |

### 数据结构

**FDeviceSnapshot** — 单个设备的信息快照：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Name` | `FString` (ReadOnly) | 设备名称 |
| `HostName` | `FString` (ReadOnly) | 设备主机名 |
| `DeviceType` | `FString` (ReadOnly) | 设备类型 |
| `ModelId` | `FString` (ReadOnly) | 设备型号标识 |
| `DeviceConnectionType` | `FString` (ReadOnly) | 连接类型 |
| `DeviceId` | `FString` (ReadOnly) | 设备唯一标识符 |
| `OperatingSystem` | `FString` (ReadOnly) | 操作系统名称 |
| `IsConnected` | `bool` (ReadOnly) | 是否已连接 |

**FDeviceSnapshots** — 设备快照数组容器（用于 TMap 值类型）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `Entries` | `TArray<FDeviceSnapshot>` (ReadOnly) | 设备快照数组 |

### 使用示例（蓝图描述）

1. 在编辑器工具蓝图中，添加一个 **Get Device Snapshots** 节点
2. 输出类型为 `TMap<FString, FDeviceSnapshots>`，键是设备类型字符串（如 `"Windows"`、`"Mac"`），值是该类型下所有设备的快照数组
3. 使用 **For Each Loop**（配合 Map 的键值对迭代）遍历设备类型
4. 对每个 `FDeviceSnapshots`，再使用 **For Each Loop** 遍历其 `Entries` 数组
5. 从每个 `FDeviceSnapshot` 中读取 `Name`、`HostName`、`IsConnected` 等字段显示或筛选设备

## C++ 用法

此插件的 C++ 接口非常简单，仅有一个静态函数。

### 头文件引入

```cpp
#include "TargetDeviceServicesBPFunctionLibrary.h"
```

### 基本用法

从头文件提取的核心用法：

```cpp
// 获取所有网络设备的快照，按设备类型分组
TMap<FString, FDeviceSnapshots> Snapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

// 遍历所有设备类型
for (const auto& Pair : Snapshots)
{
    const FString& DeviceType = Pair.Key;
    const FDeviceSnapshots& Devices = Pair.Value;
    
    UE_LOG(LogTemp, Log, TEXT("设备类型: %s, 设备数量: %d"), *DeviceType, Devices.Entries.Num());
    
    // 遍历该类型下的所有设备
    for (const FDeviceSnapshot& Device : Devices.Entries)
    {
        UE_LOG(LogTemp, Log, TEXT("  名称: %s, 主机: %s, 已连接: %s"),
            *Device.Name,
            *Device.HostName,
            Device.IsConnected ? TEXT("是") : TEXT("否"));
    }
}
```

### 进阶用法

筛选已连接的设备：

```cpp
TMap<FString, FDeviceSnapshots> Snapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

TArray<FString> ConnectedDeviceNames;

for (const auto& Pair : Snapshots)
{
    for (const FDeviceSnapshot& Device : Pair.Value.Entries)
    {
        if (Device.IsConnected)
        {
            ConnectedDeviceNames.Add(FString::Printf(TEXT("%s (%s)"), *Device.Name, *Device.OperatingSystem));
        }
    }
}
```

## Demo 示例

**注意**：此插件的 .uplugin 模块类型为 `Editor`，因此以下代码仅在编辑器环境下可用。

```cpp
// MyDeviceQueryTool.h
#pragma once

#include "CoreMinimal.h"
#include "TargetDeviceServicesBPFunctionLibrary.h"

// 查询已连接设备的辅助类
class FMyDeviceQueryTool
{
public:
    // 获取所有已连接设备的名称列表
    static TArray<FString> GetConnectedDeviceNames()
    {
        TArray<FString> Result;
        TMap<FString, FDeviceSnapshots> Snapshots = UTargetDeviceServicesBPFunctionLibrary::GetDeviceSnapshots();

        for (const auto& Pair : Snapshots)
        {
            for (const FDeviceSnapshot& Device : Pair.Value.Entries)
            {
                if (Device.IsConnected)
                {
                    Result.Add(Device.Name);
                }
            }
        }
        return Result;
    }
};
```

```cpp
// MyDeviceQueryTool.cpp
#include "MyDeviceQueryTool.h"
// 实现已在头文件中（纯静态工具类）
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TargetDeviceServices` | 底层设备服务模块，存储和管理网络设备信息 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 移除同时标记为 Experimental 和 Beta 的冗余配置 |
| 2023-11-02 | `63c9fe1c` | TargetDeviceServices - Fix long names in intermediate file names. | 修复中间文件名过长的问题 |
| 2023-11-02 | `0858844c` | TargetDeviceServices - Add plugin to be able to work with information stored in the TargetDeviceServices module via blueprints and Python. | 初始提交：创建插件以支持通过蓝图和 Python 访问 TargetDeviceServices 模块 |

### 维护评价

- **创建时间**：2023 年 11 月，插件较新
- **更新频率**：仅 3 次提交，其中 2024 年 11 月的更新仅为配置修正（移除双标记），**无实质性功能更新**
- **活跃程度**：功能极简（仅 1 个函数 + 2 个结构体），初始提交后未添加任何新 API
- **实验性标记**：`IsExperimentalVersion=true`，且 `EnabledByDefault=false`，需手动启用
- **代码规模**：仅 3 个源文件，属于极小型桥接插件

**综合评价**：此插件是一个非常轻量的实验性桥接层，将 TargetDeviceServices 模块的信息暴露给蓝图和 Python。功能单一且稳定，但自创建以来从未有过功能扩展。由于标记为实验性，**不建议在生产环境中依赖此插件**。如果仅需在编辑器工具中查询设备列表，可以作为临时方案使用，但需注意其可能在后续 UE 版本中被移除或重构。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TargetDeviceServicesScripting)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine)（未找到此插件专属文档）