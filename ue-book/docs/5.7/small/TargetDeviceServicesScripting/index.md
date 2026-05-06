# TargetDeviceServices scripting library

> Set of blueprint functions that enables working with TargetDeviceServices module via scripting

| 属性 | 值 |
|---|---|
| 中文名 | 目标设备服务脚本库 |
| 分类 | Scripting |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TargetDeviceServicesScripting` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TargetDeviceServicesScripting) | |

## 用途

该插件为蓝图提供一组可调用的函数，用于访问 `TargetDeviceServices` 模块中存储的目标设备信息。在 Unreal Editor 中，当需要自动化处理设备列表获取、设备属性查询（如名称、主机名、设备类型、操作系统、连接状态等）时，可以避免编写 C++ 代码，直接通过蓝图完成。

## 使用场景

- 你在开发自动化测试工具，需要枚举所有连接的物理设备（如 Android、iOS、游戏主机）
- 你需要根据设备型号或连接类型动态选择目标设备进行部署
- 你想在编辑器脚本或自动化蓝图中获取设备的详细信息，而无需手动解析日志或控制台输出

## 蓝图用法

插件公开的结构体和蓝图函数库主要提供设备快照数据的读取。所有数据均为只读。

### 核心数据结构

| 结构体 | 说明 | 成员 |
|---|---|---|
| `FDeviceSnapshot` | 单个设备的完整快照 | Name, HostName, DeviceType, ModelId, DeviceConnectionType, DeviceId, OperatingSystem, IsConnected |
| `FDeviceSnapshots` | 设备快照容器（用于蓝图的 `TMap` 值包装） | Entries (TArray\<FDeviceSnapshot\>) |

### 核心节点

以下节点位于蓝图函数库 `UTargetDeviceServicesBPFunctionLibrary`（脚本名称：`TargetDeviceServices`）。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Target Device Snapshots` | 获取当前所有可用设备的列表，返回 `FDeviceSnapshots` | `UTargetDeviceServicesBPFunctionLibrary` |
| `Get Target Device Snapshot` | 根据设备 ID 获取单个设备的快照，返回 `FDeviceSnapshot` | `UTargetDeviceServicesBPFunctionLibrary` |
| `Is Device Connected` | 检查指定设备当前是否已连接（返回 `bool`） | `UTargetDeviceServicesBPFunctionLibrary` |

> **注意**：节点实际名称可能因 UE 版本略有差异，请以蓝图右键菜单搜索 `TargetDeviceServices` 后列出的节点为准。

### 使用示例（蓝图）

1. **获取所有设备并输出名称**
   - 调用 `Get Target Device Snapshots` → 返回的 `FDeviceSnapshots` 展开 `Entries`。
   - 使用 `ForEachLoop` 遍历 `Entries`，从每个 `FDeviceSnapshot` 中获取 `Name` 并打印。
   - 适用于调试或动态生成设备选择 UI。

2. **检查特定设备是否在线**
   - 使用 `Get Target Device Snapshot`，输入已知的 `DeviceId`。
   - 从返回的 `FDeviceSnapshot` 读取 `IsConnected` 字段，根据结果执行后续逻辑（如自动连接）。

## C++ 用法

### 头文件引入

```cpp
#include "TargetDeviceServicesBPFunctionLibrary.h"
```

### 基本用法

```cpp
// 获取所有设备快照
UTargetDeviceServicesBPFunctionLibrary* Lib = NewObject<UTargetDeviceServicesBPFunctionLibrary>();
FDeviceSnapshots Snapshots = Lib->GetTargetDeviceSnapshots();
for (const FDeviceSnapshot& Device : Snapshots.Entries)
{
    UE_LOG(LogTemp, Log, TEXT("Device: %s - Connected: %d"), *Device.Name, Device.IsConnected);
}
```

> 来源：`TargetDeviceServicesScripting/Source/TargetDeviceServicesScripting/Public/TargetDeviceServicesBPFunctionLibrary.h`（示例为推测用法，实际函数签名请参考头文件完整声明）

## Demo 示例

一个简单的编辑器蓝图的 C++ 模拟，展示如何获取设备列表并输出到控制台。

**DeviceInfoPrinter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "TargetDeviceServicesBPFunctionLibrary.h"

class FDeviceInfoPrinter
{
public:
    static void PrintAllDevices();
};
```

**DeviceInfoPrinter.cpp**
```cpp
#include "DeviceInfoPrinter.h"

void FDeviceInfoPrinter::PrintAllDevices()
{
    UTargetDeviceServicesBPFunctionLibrary* Lib = NewObject<UTargetDeviceServicesBPFunctionLibrary>();
    FDeviceSnapshots Snapshots = Lib->GetTargetDeviceSnapshots();
    for (const FDeviceSnapshot& Device : Snapshots.Entries)
    {
        UE_LOG(LogTemp, Log, TEXT("[%s] %s (%s) - %s"),
            *Device.DeviceType, *Device.Name, *Device.HostName,
            Device.IsConnected ? TEXT("Connected") : TEXT("Disconnected"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TargetDeviceServices` | 提供底层的设备发现与管理服务 |

其他依赖均为标准 Core/Engine 模块，不额外列出。

## 维护状态

### 近期更新

- 2024-11-22 `36771d79` Updated uplugin descriptor files marked as both Experimental and Beta – 元数据字段更新，移除重复标记
- 2023-11-02 `63c9fe1c` TargetDeviceServices - Fix long names in intermediate file names – 修复长文件名问题
- 2023-11-02 `0858844c` TargetDeviceServices - Add plugin to be able to work with information stored in the TargetDeviceServices module – 插件初始创建

### 维护评价

- **创建时间**：2023-11-02，距今约 2 年
- **最近更新**：2024-11-22，仍有元数据维护，但无功能更新
- **活跃度**：低。插件自创建后仅有一次描述修复，未添加新功能或修复逻辑 Bug
- **已知限制**：插件处于实验阶段（`IsExperimentalVersion = true`），默认未启用，需要手动在 Plugin 列表启用；API 可能在未来版本发生变化或移除
- **推荐度**：仅在明确需要从蓝图访问设备信息时使用。如果项目只用 C++，建议直接使用 `TargetDeviceServices` 模块原生 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/TargetDeviceServicesScripting)
- [官方文档](无)
- [测试用例](无，插件未包含测试代码)