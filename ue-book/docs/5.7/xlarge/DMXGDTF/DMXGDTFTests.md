# DMX GDTF

> Implementation of the GDTF standard using Unreal Engine types

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXGDTF` (Runtime), `DMXGDTFTests` (Editor), `DMXZip` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF) | |

## 用途

本插件的核心功能是**解析和实现 GDTF (General Device Type Format) 标准**。GDTF 是一种用于描述舞台灯光、效果器等设备控制参数的开放性 XML 文件格式。该插件将 GDTF 文件中的设备描述（如 DMX 通道、模式、属性、几何结构等）转换为 Unreal Engine 内部的类型和数据结构，使得 UE 能够理解并控制符合 GDTF 标准的灯光设备。

它解决了虚拟制作流程中，不同厂商的灯光设备需要统一描述和控制的问题。通过此插件，用户可以导入制造商提供的 `.gdtf` 文件，从而在 UE 中获得标准化的设备控制接口，无需为每款设备手动配置 DMX 映射。

## 使用场景

- **虚拟制作灯光控制**：在虚拟影棚中，需要精确控制各种品牌和型号的灯光设备。使用本插件导入对应的 GDTF 文件，即可在 UE 中通过 DMX 协议控制这些设备。
- **预可视化 (Previz)**：在项目前期，使用 GDTF 文件在 UE 中模拟真实灯光设备的控制方式和效果，进行灯光设计和编程。
- **标准化资产管线**：建立基于 GDTF 标准的灯光设备资产库，确保团队内部和与外部供应商之间的设备描述一致性。

## 蓝图用法

本插件主要提供运行时数据解析和资产创建功能，蓝图接口相对底层，通常用于构建上层工具或自动化流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create GDTF Asset` | 从 GDTF 文件内容创建 `UGDTFAsset` 资产 | `UGDTFAssetFactory` |
| `Get GDTF Subsystem` | 获取管理 GDTF 资产的子系统实例 | `UGDTFSubsystem` |
| `Parse GDTF File` | 解析 GDTF XML 文件内容，返回根节点对象 | `UGDTFXmlNode` |
| `Get Fixture Type` | 从 GDTF 资产中获取指定的灯具类型描述 | `UGDTFAsset` |
| `Get DMX Mode` | 从灯具类型中获取指定的 DMX 模式 | `UGDTFFixtureType` |

### 使用示例（蓝图描述）

1.  **创建 GDTF 资产**：使用 `Create GDTF Asset` 节点，输入 GDTF 文件的二进制数据（通常通过文件读取获得），即可在内容浏览器中生成一个 `UGDTFAsset`。
2.  **查询设备信息**：从创建的 `UGDTFAsset` 中，可以调用 `Get Fixture Type` 获取设备类型，再进一步调用 `Get DMX Mode` 获取具体的 DMX 通道布局信息，用于后续的 DMX 映射或 UI 生成。

## C++ 用法

### 头文件引入

```cpp
#include “DMXGDTFModule.h”
#include “GDTFAsset.h”
#include “GDTFFixtureType.h”
#include “GDTFXmlNode.h”
```

### 基本用法

以下示例展示了如何解析一个 GDTF 文件并获取其基本信息。

```cpp
// 来源: Engine/Plugins/VirtualProduction/DMX/DMXGDTF/Source/DMXGDTFTests/Private/Tests/GDTFAssetTest.cpp
void ParseGDTFFile(const TArray<uint8>& FileData)
{
    // 1. 解析 GDTF XML 文件内容
    TSharedRef<FGDTFXmlNode> RootNode = FGDTFXmlNode::Parse(FileData);
    if (!RootNode.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT(“Failed to parse GDTF file.”));
        return;
    }

    // 2. 从根节点创建 GDTF 资产对象
    UGDTFAsset* GDTFAsset = NewObject<UGDTFAsset>();
    GDTFAsset->InitializeFromXmlNode(RootNode);

    // 3. 访问解析后的数据
    if (GDTFAsset->FixtureTypes.Num() > 0)
    {
        const UGDTFFixtureType* FirstFixtureType = GDTFAsset->FixtureTypes[0];
        UE_LOG(LogTemp, Log, TEXT(“Fixture Type Name: %s”), *FirstFixtureType->Name);
        
        if (FirstFixtureType->DMXModes.Num() > 0)
        {
            const UGDTFDMXMode* FirstMode = FirstFixtureType->DMXModes[0];
            UE_LOG(LogTemp, Log, TEXT(“First DMX Mode: %s, Channels: %d”), *FirstMode->Name, FirstMode->DMXChannels.Num());
        }
    }
}
```

### 进阶用法

结合 `DMXZip` 模块处理 `.gdtf` 压缩包（GDTF 文件通常是 ZIP 格式）。

```cpp
// 来源: Engine/Plugins/VirtualProduction/DMX/DMXGDTF/Source/DMXGDTFTests/Private/Tests/GDTFZipTest.cpp
#include “DMXZipModule.h”
#include “ZipFile.h”

void LoadGDTFFromZip(const FString& ZipFilePath)
{
    // 1. 使用 DMXZip 模块解压文件
    FDMXZipModule& ZipModule = FModuleManager::GetModuleChecked<FDMXZipModule>(“DMXZip”);
    TSharedPtr<FZipFile> ZipFile = ZipModule.CreateZipFileFromFile(ZipFilePath);
    if (!ZipFile.IsValid())
    {
        return;
    }

    // 2. 从 ZIP 中提取 GDTF XML 文件（通常名为 description.xml）
    TArray<uint8> XMLData;
    if (ZipFile->ExtractFile(“description.xml”, XMLData))
    {
        // 3. 调用之前的解析函数
        ParseGDTFFile(XMLData);
    }
}
```

## Demo 示例

一个完整的最小示例，展示如何创建一个简单的 GDTF 资产工厂。

```cpp
// MyGDTFAssetFactory.h
#pragma once
#include “Factories/Factory.h”
#include “MyGDTFAssetFactory.generated.h”

UCLASS()
class UMyGDTFAssetFactory : public UFactory
{
    GENERATED_BODY()
public:
    UMyGDTFAssetFactory();
    virtual UObject* FactoryCreateBinary(UClass* Class, UObject* InParent, FName Name, EObjectFlags Flags, UObject* Context, const TCHAR* Type, const uint8*& Buffer, const uint8* BufferEnd, FFeedbackContext* Warn) override;
    virtual bool FactoryCanImport(const FString& Filename) override;
};
```

```cpp
// MyGDTFAssetFactory.cpp
#include “MyGDTFAssetFactory.h”
#include “GDTFAsset.h”
#include “GDTFXmlNode.h”

UMyGDTFAssetFactory::UMyGDTFAssetFactory()
{
    SupportedClass = UGDTFAsset::StaticClass();
    bCreateNew = false;
    bEditorImport = true;
    Formats.Add(TEXT(“gdtf;GDTF File”));
}

bool UMyGDTFAssetFactory::FactoryCanImport(const FString& Filename)
{
    return FPaths::GetExtension(Filename).Equals(TEXT(“gdtf”), ESearchCase::IgnoreCase);
}

UObject* UMyGDTFAssetFactory::FactoryCreateBinary(UClass* Class, UObject* InParent, FName Name, EObjectFlags Flags, UObject* Context, const TCHAR* Type, const uint8*& Buffer, const uint8* BufferEnd, FFeedbackContext* Warn)
{
    // 将二进制数据转换为字节数组
    TArray<uint8> FileData;
    FileData.Append(Buffer, BufferEnd - Buffer);

    // 解析并创建资产
    TSharedRef<FGDTFXmlNode> RootNode = FGDTFXmlNode::Parse(FileData);
    if (!RootNode.IsValid())
    {
        return nullptr;
    }

    UGDTFAsset* NewAsset = NewObject<UGDTFAsset>(InParent, Class, Name, Flags);
    NewAsset->InitializeFromXmlNode(RootNode);
    return NewAsset;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXLibrary` | 提供 DMX 协议和设备库的基础支持 |
| `ZipUtility` | 提供 ZIP 文件压缩和解压功能，用于处理 `.gdtf` 包 |

## 维护状态

### 近期更新

```
- 9f2176214dc5 DMX: Fix incompatible module names preventing modules from being loaded correctly at launch.
- 4a69ec709e89 DMX - Fix CIS error pragma once in main file
- 8e75e2dae524 DMX - Add GDTF export functinality, unit testing, improve GDTF data structure
```

- `9f2176214dc5`: 修复了模块名称不兼容导致启动时加载失败的问题，属于重要的兼容性修复。
- `4a69ec709e89`: 修复了代码静态分析（CIS）错误，提升了代码质量。
- `8e75e2dae524`: **功能性更新**，增加了 GDTF 导出功能、单元测试，并改进了 GDTF 数据结构。这表明插件在积极开发和完善中。

### 维护评价

- **创建时间**：插件于 2024 年 4 月创建，非常新。
- **最近更新**：最近的提交（2024年）包含了重要的功能添加（导出）和稳定性修复，表明处于**活跃维护**状态。
- **已知限制**：作为较新的插件，其 API 和功能可能仍在演进中。`.uplugin` 中 `Hidden: true` 表明它可能尚未作为独立功能向所有用户公开，而是作为 DMX 插件套件的内部组件。
- **推荐使用**：**推荐**。对于需要在 UE 中集成 GDTF 标准灯光设备的虚拟制作项目，这是一个官方且正在积极维护的解决方案。建议关注其后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF/Source/DMXGDTFTests)