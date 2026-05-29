# DMX GDTF

> Implementation of the GDTF standard using Unreal Engine types

| 属性 | 值 |
|---|---|
| 中文名 | DMX 通用设备类型格式 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXGDTF` (Runtime), `DMXGDTFTests` (Editor), `DMXZip` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF) | |

## 用途

DMXGDTF 插件是一个完整的 GDTF (通用设备类型格式) 标准实现，旨在将 GDTF 文件规范（一种描述舞台、影视照明设备特性的 XML 文件格式）映射到虚幻引擎的 C++ 类型系统中。它的核心目标是：

1.  **数据解析与映射**：将 GDTF XML 文件（或其包含在 ZIP 中的 `description.xml`）解析成一套结构化的、易于在 UE 中操作的 C++ 对象树（例如 `FDMXGDTFFixtureType`, `FDMXGDTFGeometry` 等）。
2.  **标准化抽象**：提供一套符合 GDTF 1.1/1.2 标准的数据结构，覆盖设备模型、几何结构、DMX 通道模式、物理属性（光源、滤色片）、轮盘、协议等所有方面，使得 UE 内的 DMX 工具可以基于这套标准数据工作。
3.  **数据操作与序列化**：支持从 `UDMXGDTF` 对象重新导出（序列化）为标准的 GDTF XML 文件，实现了数据的双向兼容。
4.  **提供底层支持**：为更高级别的 DMX 工具（如 DMX 清单导入器、灯具可视化预览）提供基础的 GDTF 数据层。

简单来说，它解决了虚拟制片和现场娱乐行业中，不同厂商的照明设备如何在虚幻引擎中被统一描述、导入和操作的根本问题，是 UE 虚拟灯光工作流的基石组件之一。

## 使用场景

-   你正在构建一个虚拟制片场景，需要精确控制连接到 UE 的实体灯光设备（如 MA Lighting grandMA3 控制台管理的灯具）。你需要从灯具制造商处获取其 GDTF 文件，以便在 UE 的 DMX 编辑器中正确映射 DMX 通道和功能。此插件负责加载和解析该 GDTF 文件。
-   你开发了一个自定义的灯光设计工具或插件，需要读取、验证或修改 GDTF 文件中定义的设备属性（如光束角度、色温、轮盘内容），此插件提供了完整的对象模型。
-   你需要为 UE 的 `DMXFixtureActor` 或类似的蓝图 actor 动态生成基于 GDTF 数据的逻辑，例如，根据 GDTF 中定义的 `DMXMode` 来设置和控制灯具。
-   你正在编写一个 GDTF 文件编辑器或查看器，运行于 UE 编辑器内部。

## 蓝图用法

该插件主要提供底层数据结构和 C++ API。从源码分析，`UDMXGDTF` 类是主要的 UObject 接口，但其大部分功能是面向数据和 C++ 开发者的。**注意**：在 `.uplugin` 中该插件被标记为 `Hidden: true`，通常意味着它不直接在内容浏览器中暴露资产类型，更多是作为其他 DMX 工具（如 DMX 编辑器）的依赖模块存在。蓝图直接使用的高级接口较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize From Data` | 从 `.gdtf` 文件的原始字节数据初始化 GDTF 描述。 | `UDMXGDTF` |
| `Export As Xml` | 将当前的 GDTF 数据结构导出为 `FXmlFile` 对象。 | `UDMXGDTF` |
| `Get Description` | 获取当前 GDTF 描述（`FDMXGDTFDescription`）的共享引用。 | `UDMXGDTF` |

### 使用示例（蓝图描述）
由于插件为隐藏模块且主要提供数据结构，蓝图中的典型使用模式是：
1.  在 C++ 中获取一个 `UDMXGDTF*` 对象（可能来自 DMX 导入工具创建的资产）。
2.  通过 C++ 代码调用 `InitializeFromData` 或 `InitializeFromFixtureType` 来填充数据。
3.  在 C++ 中遍历其内部的 `FDMXGDTFFixtureType` 及其子对象（如 `DMXModes`, `Geometries`）来获取所需信息。
蓝图更可能通过其他更高级的 DMX 蓝图节点（如 `Get Fixture Patch List`）间接使用此插件解析的结果，而不是直接操作 `UDMXGDTF` 对象。

## C++ 用法

### 头文件引入
```cpp
#include "DMXGDTF.h"
// 访问具体GDTF数据类型通常需要引入对应头文件，例如：
#include "GDTF/DMXGDTFFixtureType.h"
#include "GDTF/DMXModes/DMXGDTFDMXMode.h"
#include "GDTF/Geometries/DMXGDTFGeometry.h"
```

### 基本用法
从测试用例和接口定义中提取的基本初始化和访问流程。
```cpp
// 假设你已有一段 .gdtf 文件的原始数据 (TArray64<uint8>)
TArray64<uint8> GDTFRawData = ...; // 从文件或网络加载

// 创建 UDMXGDTF 对象并初始化
UDMXGDTF* GDTFObject = NewObject<UDMXGDTF>();
GDTFObject->InitializeFromData(GDTFRawData);

// 获取解析后的 FixtureType 数据
TSharedPtr<UE::DMX::GDTF::FDMXGDTFFixtureType> FixtureType = GDTFObject->GetDescription()->GetFixtureType();
if (FixtureType.IsValid())
{
    // 打印设备名称和制造商
    UE_LOG(LogTemp, Log, TEXT("Fixture: %s, Manufacturer: %s"), *FixtureType->Name.ToString(), *FixtureType->Manufacturer);
    
    // 列出所有 DMX 模式
    for (const auto& DMXMode : FixtureType->DMXModes)
    {
        UE_LOG(LogTemp, Log, TEXT("  DMX Mode: %s"), *DMXMode->Name.ToString());
    }
}
```
*(来源：基于 `UDMXGDTF` 类接口和通用 GDTF 数据访问模式)*

### 进阶用法
访问特定模式下的通道信息和几何关系。
```cpp
// ... 接上面的代码，已获取 FixtureType
if (FixtureType.IsValid() && FixtureType->DMXModes.Num() > 0)
{
    // 获取第一个DMX模式
    auto FirstDMXMode = FixtureType->DMXModes[0];
    
    // 遍历该模式下的所有DMX通道
    for (const auto& DMXChannel : FirstDMXMode->DMXChannels)
    {
        // 解析该通道关联的几何体
        TSharedPtr<UE::DMX::GDTF::FDMXGDTFGeometry> LinkedGeometry = DMXChannel->ResolveGeometry();
        if (LinkedGeometry.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("Channel '%s' controls geometry '%s'"), 
                *DMXChannel->Geometry.ToString(), *LinkedGeometry->Name.ToString());
        }
        
        // 获取逻辑通道和属性
        for (const auto& LogicalChannel : DMXChannel->LogicalChannelArray)
        {
            TSharedPtr<UE::DMX::GDTF::FDMXGDTFAttribute> Attribute = LogicalChannel->ResolveAttribute();
            if (Attribute.IsValid())
            {
                UE_LOG(LogTemp, Log, TEXT("  Logical Channel Attribute: %s"), *Attribute->Name.ToString());
            }
        }
    }
}
```
*(来源：综合 `FDMXGDTFDMXChannel`、`FDMXGDTFLogicalChannel` 及其 `Resolve*` 方法)*

## Demo 示例
一个完整的、可编译的最小示例，展示如何从数据初始化 GDTF 并获取基本信息。

**GDTFDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DMXGDTF.h" // 核心头文件

class UDMXGDTF;

class FGDTFDemo
{
public:
    /** 初始化并查询一个GDTF对象 */
    static void InitializeAndQueryGDTF(const TArray64<uint8>& InGDTFData);
};
```

**GDTFDemo.cpp**
```cpp
#include "GDTFDemo.h"
#include "DMXGDTF.h"
#include "GDTF/DMXGDTFFixtureType.h" // 需要访问FixtureType结构

void FGDTFDemo::InitializeAndQueryGDTF(const TArray64<uint8>& InGDTFData)
{
    // 1. 创建DMXGDTF UObject
    UDMXGDTF* GDTFAsset = NewObject<UDMXGDTF>();
    if (!GDTFAsset)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create UDMXGDTF object"));
        return;
    }

    // 2. 从原始数据初始化
    GDTFAsset->InitializeFromData(InGDTFData);
    
    // 3. 访问解析后的数据
    TSharedPtr<UE::DMX::GDTF::FDMXGDTFDescription> Description = GDTFAsset->GetDescription();
    if (!Description.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("GDTF data is invalid or could not be parsed."));
        return;
    }

    TSharedPtr<UE::DMX::GDTF::FDMXGDTFFixtureType> FixtureType = Description->GetFixtureType();
    if (FixtureType.IsValid())
    {
        UE_LOG(LogTemp, Display, TEXT("Successfully parsed GDTF fixture: %s (Manufacturer: %s)"),
            *FixtureType->LongName.ToString(), *FixtureType->Manufacturer);
        UE_LOG(LogTemp, Display, TEXT("  - Has %d DMX Mode(s)"), FixtureType->DMXModes.Num());
        UE_LOG(LogTemp, Display, TEXT("  - Has %d Model(s)"), FixtureType->Models.Num());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("GDTF description does not contain a valid FixtureType."));
    }
    
    // 4. (可选) 将修改后的数据导出回XML
    TSharedPtr<FXmlFile> ExportedXml = GDTFAsset->ExportAsXml();
    if (ExportedXml.IsValid())
    {
        UE_LOG(LogTemp, Display, TEXT("GDTF data successfully exported to XML."));
        // 这里可以使用 ExportedXml->GetContent() 获取字符串内容并保存。
    }
}
```

## 模块依赖
从插件名称和上下文推断，此插件的依赖相对标准。主要依赖包括用于 XML 解析的 `XmlParser` 模块。使用此插件时，你的项目或模块通常需要：

| 模块 | 用途 |
|---|---|
| `XmlParser` | 用于解析 GDTF 文件中的 XML 内容 (`FXmlFile`)。 |
| `DMXGDTF` (本插件 Runtime 模块) | 访问所有 GDTF 数据结构和 `UDMXGDTF` 类。 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正格式说明符与64位/32位参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的 UE_LOGF 宏。 |
| 2026-02-02 | `f5e86e73` | DMXGDTF: Fix potential divide by zero | 修复一处潜在的除以零错误。 |
| 2024-09-26 | `62a80188` | DMX: Move the DMXGDTF header from internal to public | 将 DMXGDTF 主要头文件从内部移至公共目录，提升 API 可见性。 |

### 维护评价
-   **创建时间**：该插件于 2024 年 4 月创建，是一个相对较新的组件。
-   **近期活动**：最近一次代码更新（提交哈希 `852b276c`）发生在 2026 年 5 月，主要是一系列代码质量、可移植性和警告修复。这表明插件仍在积极维护中，但近期没有添加重大新功能。
-   **维护状态**：**维护中**。插件由 Epic Games 官方维护，持续集成到引擎主线，确保其与最新 UE 版本兼容。其作为 DMX 工具链基础模块的重要性决定了它不会轻易被废弃。
-   **已知限制**：作为底层数据解析库，其稳定性很高。主要限制在于它不提供完整的用户界面，使用门槛较高，需要开发者熟悉 GDTF 标准。
-   **推荐使用**：**强烈推荐**在任何涉及专业 DMX 灯光控制的虚拟制片项目中使用。它是连接实体灯光硬件与虚幻引擎的官方标准桥梁，功能完整且得到持续维护。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF)
- [官方文档](https://gdtf-share.com/)（GDTF 标准及文件共享平台）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXGDTF/Source/DMXGDTFTests)