# DMX GDTF

> Implementation of the GDTF standard using Unreal Engine types

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXGDTF` (Runtime), `DMXGDTFTests` (Editor), `DMXZip` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF) | |

## 用途

DMX GDTF 插件是 **GDTF (General Device Type Format)** 标准在 Unreal Engine 中的实现。GDTF 是一种用于描述舞台灯光、媒体服务器等专业灯光设备的 XML 文件格式标准，它定义了设备的几何结构、DMX 通道映射、物理属性、颜色信息等。

该插件的核心作用是**解析和表示 GDTF 文件**，将标准的 GDTF XML 数据转换为 Unreal Engine 内部的 C++ 对象模型。这使得 Unreal Engine 的虚拟制作（Virtual Production）工具链能够：
1.  **导入和理解**第三方灯光设备制造商提供的标准化设备描述文件。
2.  **基于标准描述**在引擎内准确地创建和控制虚拟灯光设备。
3.  **确保不同软件和硬件**之间关于设备能力的描述一致性，是构建专业级虚拟影棚灯光控制系统的基础。

## 使用场景

-   你在搭建一个**虚拟影棚**，需要将真实的灯光设备（如摇头灯、LED 面板）的精确控制参数导入到 Unreal Engine 中，以便在虚拟场景中进行匹配和预演。
-   你正在开发一个**灯光控制台软件**或**媒体服务器**的 UE5 插件，需要读取和理解 GDTF 文件来获取设备的通道布局和功能。
-   你需要从 GDTF 文件中提取设备的**3D 模型信息**（几何结构）和**物理属性**（如重量、功率、色温范围），用于场景中的资产管理和物理模拟。
-   你希望利用 **MVR (My Virtual Rig)** 工作流，而 GDTF 是 MVR 中描述设备部分的核心标准。

## 蓝图用法

该插件主要为 C++ 层提供 GDTF 数据解析和访问能力，其核心类（如 `FDMXGDTFFixtureType`）并非 UObject，因此**不直接暴露为蓝图节点**。然而，它提供了一些可在蓝图中使用的数据结构。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FDMXGDTFColorCIE1931xyY` | 一个蓝图可用的结构体，用于表示 CIE 1931 xyY 颜色空间中的颜色，常用于 GDTF 和 MVR 标准。 | `FDMXGDTFColorCIE1931xyY` |

### 使用示例（蓝图描述）

在蓝图中，你可以创建 `FDMXGDTFColorCIE1931xyY` 类型的变量，并设置其 `X`、`Y`、`YY` 属性来表示一个颜色。这个结构体主要用于在蓝图和 C++ 之间传递 GDTF 相关的颜色数据，但解析 GDTF 文件本身的操作需要在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "DMXGDTFModule.h" // 主模块头文件
#include "GDTF/DMXGDTFFixtureType.h" // 设备类型根节点
#include "GDTF/Geometries/DMXGDTFGeometryCollect.h" // 几何集合
#include "GDTF/AttributeDefinitions/DMXGDTFAttributeDefinitions.h" // 属性定义
```

### 基本用法

以下示例展示了如何加载并解析一个 GDTF 文件，并访问其设备类型信息。
*(来源: `Engine/Plugins/VirtualProduction/DMX/DMXGDTF/Source/DMXGDTFTests/Private/Tests/DMXGDTFTests.cpp`)*

```cpp
// 假设 GDTF 文件内容已加载到 FString GDTFFileContent 中
FString GDTFFileContent = TEXT("..."); // 从文件或网络加载的 GDTF XML 内容

// 使用 GDTF 模块提供的工具函数解析 XML 字符串
TSharedPtr<UE::DMX::GDTF::FDMXGDTFFixtureType> FixtureType = UE::DMX::GDTF::FDMXGDTFXmlNodeBuilder::CreateFixtureTypeFromXml(GDTFFileContent);

if (FixtureType.IsValid())
{
    // 获取设备类型名称
    FName FixtureTypeName = FixtureType->Name;
    UE_LOG(LogTemp, Log, TEXT("Parsed GDTF Fixture Type: %s"), *FixtureTypeName.ToString());

    // 访问几何集合
    TSharedPtr<UE::DMX::GDTF::FDMXGDTFGeometryCollect> GeometryCollect = FixtureType->GeometryCollect;
    if (GeometryCollect.IsValid())
    {
        // 遍历几何集合中的子几何（示例）
        for (const TSharedPtr<UE::DMX::GDTF::FDMXGDTFGeometry>& Geometry : GeometryCollect->GeometryArray)
        {
            UE_LOG(LogTemp, Log, TEXT("  Geometry: %s (Tag: %s)"), *Geometry->Name.ToString(), Geometry->GetXmlTag());
        }
    }

    // 访问属性定义
    TSharedPtr<UE::DMX::GDTF::FDMXGDTFAttributeDefinitions> AttributeDefinitions = FixtureType->AttributeDefinitions;
    if (AttributeDefinitions.IsValid())
    {
        // 可以进一步访问 FeatureGroups, Attributes 等
    }
}
```

### 进阶用法

结合多个部分，遍历一个设备类型的所有 DMX 模式及其通道函数。
*(综合自多个测试用例和头文件结构)*

```cpp
if (FixtureType.IsValid())
{
    // 遍历所有 DMX 模式
    for (const TSharedPtr<UE::DMX::GDTF::FDMXGDTFDMXMode>& DMXMode : FixtureType->DMXModeArray)
    {
        UE_LOG(LogTemp, Log, TEXT("DMX Mode: %s"), *DMXMode->Name.ToString());

        // 遍历该模式下的所有通道
        for (const TSharedPtr<UE::DMX::GDTF::FDMXGDTFDMXChannel>& DMXChannel : DMXMode->DMXChannelArray)
        {
            // 获取通道的 DMX 地址
            FDMXGDTFDMXAddress Address = DMXChannel->DMXAddress;
            UE_LOG(LogTemp, Log, TEXT("  Channel: %s, Universe: %d, Address: %d"),
                *DMXChannel->Name.ToString(), Address.GetUniverse(), Address.GetChannel());

            // 遍历通道函数
            for (const TSharedPtr<UE::DMX::GDTF::FDMXGDTFChannelFunction>& ChannelFunction : DMXChannel->ChannelFunctionArray)
            {
                UE_LOG(LogTemp, Log, TEXT("    Function: %s, Attribute: %s"),
                    *ChannelFunction->Name.ToString(), *ChannelFunction->Attribute.ToString());
            }
        }
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何解析 GDTF 文件并打印设备基本信息。

### GDTFDemo.h
```cpp
#pragma once

#include "CoreMinimal.h"

class FGDTFDemo
{
public:
    /** 解析 GDTF 文件内容并打印信息 */
    static void ParseAndPrintGDTF(const FString& GDTFXmlContent);
};
```

### GDTFDemo.cpp
```cpp
#include "GDTFDemo.h"
#include "DMXGDTFModule.h"
#include "GDTF/DMXGDTFFixtureType.h"
#include "GDTF/Geometries/DMXGDTFGeometryCollect.h"
#include "GDTF/DMXGDTFXmlNodeBuilder.h"

void FGDTFDemo::ParseAndPrintGDTF(const FString& GDTFXmlContent)
{
    // 使用插件提供的构建器解析 XML
    TSharedPtr<UE::DMX::GDTF::FDMXGDTFFixtureType> FixtureType =
        UE::DMX::GDTF::FDMXGDTFXmlNodeBuilder::CreateFixtureTypeFromXml(GDTFXmlContent);

    if (!FixtureType.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to parse GDTF content."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("=== GDTF Device Info ==="));
    UE_LOG(LogTemp, Log, TEXT("Name: %s"), *FixtureType->Name.ToString());
    UE_LOG(LogTemp, Log, TEXT("Manufacturer: %s"), *FixtureType->Manufacturer.ToString());

    // 打印几何结构概览
    if (FixtureType->GeometryCollect.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Geometry Count: %d"), FixtureType->GeometryCollect->GeometryArray.Num());
    }

    // 打印 DMX 模式数量
    UE_LOG(LogTemp, Log, TEXT("DMX Mode Count: %d"), FixtureType->DMXModeArray.Num());

    UE_LOG(LogTemp, Log, TEXT("========================"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXZip` | 处理 GDTF 文件的 `.gdtf` 压缩包格式（本质是 ZIP）。 |
| `XmlParser` | 解析 GDTF 文件中的 XML 数据。 |
| `Json` | 可能用于处理 GDTF 相关元数据或配置。 |

## 维护状态

### 近期更新

-   3a61bfb83396 DMX: Move the DMXGDTF header from internal to public
    *将 DMXGDTF 的头文件从内部目录移动到公共目录，使其可以被其他插件和模块引用。*
-   e640b90af8e5 DMX: Move Unreal's GDTF API from internal to public
    *将 Unreal 的 GDTF API 从内部移动到公共，标志着该插件的 API 趋于稳定并准备对外提供。*
-   d561ab1d15b2 DMX: Improvments and bug fixes for MVR and GDTF
    *对 MVR 和 GDTF 进行了改进和错误修复。*

### 维护评价

-   **活跃维护**：插件创建于 2024 年 4 月，非常年轻。最近的提交（2025 年）显示 Epic Games 正在积极地将其 API 公开化并修复问题，表明它处于**活跃开发**阶段。
-   **实验性/隐藏**：尽管 `.uplugin` 中 `IsExperimentalVersion` 为 `false`，但 `Hidden: true` 和 `EnabledByDefault: false` 表明它目前仍被视为一个**内部或高级功能**，尚未作为标准功能向所有用户开放。
-   **推荐使用**：如果你正在开发专业的虚拟制作灯光工具链，并且需要与 GDTF 标准集成，那么这个插件是**必不可少且推荐使用**的。对于普通游戏开发，通常不需要直接使用此插件。请注意其 API 可能随着版本更新而变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF/Source/DMXGDTFTests)