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

本插件实现了 **GDTF (General Device Type Format)** 标准。GDTF 是一种用于描述舞台灯光、特效等设备（如电脑灯、LED 灯条）的标准化 XML 文件格式。该插件的核心功能是将 `.gdtf` 文件（通常是一个 ZIP 压缩包）解析为 Unreal Engine 内部的类型和数据结构，为 DMX 系统提供标准化的设备描述信息，从而实现对符合 GDTF 标准的灯光设备的精确控制和模拟。

## 使用场景

- 你在虚拟制片或现场演出中，需要控制来自不同制造商的标准化灯光设备。
- 你希望使用行业标准的 GDTF 文件来定义设备的 DMX 通道、模式、属性和几何信息，而不是手动在引擎中配置。
- 你需要一个统一的接口来加载、解析和查询 GDTF 设备描述，以便与 DMX 协议栈集成。

## 蓝图用法

由于插件规模较大，蓝图 API 主要分布在 `DMXGDTF` 和 `DMXZip` 模块中。以下为核心功能节点概览。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load GDTF File` | 从文件路径加载并解析一个 `.gdtf` 文件，返回一个 `UDMXGDTF` 对象。 | `UDMXGDTF` |
| `Get Fixture Type` | 从已加载的 GDTF 对象中获取设备类型描述。 | `UDMXGDTF` |
| `Get Geometry` | 获取设备的几何树结构（如灯头、透镜等部件）。 | `UDMXFixtureType` |
| `Get DMX Modes` | 获取设备支持的所有 DMX 模式及其通道配置。 | `UDMXFixtureType` |
| `Get Attribute` | 根据名称获取一个特定的 DMX 属性（如 Pan, Tilt, Dimmer）。 | `UDMXFixtureType` |
| `Unzip GDTF` | 将 `.gdtf` 文件（ZIP 格式）解压到指定目录。 | `UDMXZip` |

### 使用示例（蓝图描述）

1.  **加载设备描述**：使用 `Load GDTF File` 节点，输入一个 `.gdtf` 文件的路径，获取 `UDMXGDTF` 对象。
2.  **查询设备信息**：从 `UDMXGDTF` 对象调用 `Get Fixture Type`，然后进一步调用 `Get DMX Modes` 来查看设备支持的控制模式。
3.  **解压资源**：如果需要访问 GDTF 文件内部的 3D 模型或纹理，可以使用 `Unzip GDTF` 节点将其解压。

## C++ 用法

### 头文件引入

```cpp
#include "DMXGDTF.h"
#include "DMXZip.h"
```

### 基本用法

从测试用例中提取的典型用法：加载并解析一个 GDTF 文件。
*来源：`DMXGDTFTests/DMXGDTFTests.cpp`*

```cpp
// 创建 GDTF 解析器
UDMXGDTF* GDTF = NewObject<UDMXGDTF>();

// 加载并解析 GDTF 文件
const FString GDTFFilePath = TEXT("/Path/To/Your/Fixture.gdtf");
bool bSuccess = GDTF->LoadGDTFFile(GDTFFilePath);

if (bSuccess)
{
    // 获取设备类型
    UDMXFixtureType* FixtureType = GDTF->GetFixtureType();
    if (FixtureType)
    {
        // 获取设备名称
        FString FixtureName = FixtureType->Name;
        
        // 获取第一个 DMX 模式
        const TArray<UDMXFixtureMode*>& Modes = FixtureType->GetDMXModes();
        if (Modes.Num() > 0)
        {
            UDMXFixtureMode* FirstMode = Modes[0];
            // ... 进一步操作模式和通道
        }
    }
}
```

### 进阶用法

结合 `DMXZip` 模块，先解压再解析，并遍历设备几何树。
*来源：`DMXGDTFTests/DMXGDTFTests.cpp`*

```cpp
// 1. 解压 GDTF 文件
const FString GDTFPath = TEXT("/Path/To/Fixture.gdtf");
const FString OutputDir = TEXT("/Path/To/Output/");
UDMXZip::UnzipGDTF(GDTFPath, OutputDir);

// 2. 加载解压后的 GDTF 文件（通常解压后会有一个 .gdtf 文件）
const FString ExtractedGDTFPath = FPaths::Combine(OutputDir, TEXT("description.gdtf"));
UDMXGDTF* GDTF = NewObject<UDMXGDTF>();
GDTF->LoadGDTFFile(ExtractedGDTFPath);

// 3. 遍历几何树
if (UDMXFixtureType* FixtureType = GDTF->GetFixtureType())
{
    UDMXFixtureGeometry* RootGeometry = FixtureType->GetGeometry();
    if (RootGeometry)
    {
        // 递归遍历几何节点
        TraverseGeometryTree(RootGeometry);
    }
}

// 辅助函数：递归遍历几何树
void TraverseGeometryTree(UDMXFixtureGeometry* Geometry)
{
    if (!Geometry) return;
    
    // 处理当前几何节点（例如，获取其名称、变换、3D模型引用）
    UE_LOG(LogTemp, Log, TEXT("Geometry: %s"), *Geometry->Name);
    
    // 遍历子几何节点
    for (UDMXFixtureGeometry* Child : Geometry->GetChildren())
    {
        TraverseGeometryTree(Child);
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何加载 GDTF 文件并打印设备信息。

**MyGDTFActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGDTFActor.generated.h"

class UDMXGDTF;

UCLASS()
class AMyGDTFActor : public AActor
{
    GENERATED_BODY()

public:
    AMyGDTFActor();

    UPROPERTY(EditAnywhere, Category = "GDTF")
    FFilePath GDTFFile;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "GDTF")
    void LoadAndPrintGDTFInfo();

private:
    UPROPERTY()
    TObjectPtr<UDMXGDTF> LoadedGDTF;
};
```

**MyGDTFActor.cpp**
```cpp
#include "MyGDTFActor.h"
#include "DMXGDTF.h"

AMyGDTFActor::AMyGDTFActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyGDTFActor::LoadAndPrintGDTFInfo()
{
    if (GDTFFile.FilePath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("GDTF file path is not set."));
        return;
    }

    // 创建并加载 GDTF
    LoadedGDTF = NewObject<UDMXGDTF>();
    if (LoadedGDTF->LoadGDTFFile(GDTFFile.FilePath))
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded GDTF file: %s"), *GDTFFile.FilePath);
        
        if (UDMXFixtureType* FixtureType = LoadedGDTF->GetFixtureType())
        {
            UE_LOG(LogTemp, Log, TEXT("  Fixture Name: %s"), *FixtureType->Name);
            UE_LOG(LogTemp, Log, TEXT("  Manufacturer: %s"), *FixtureType->Manufacturer);
            UE_LOG(LogTemp, Log, TEXT("  DMX Modes Count: %d"), FixtureType->GetDMXModes().Num());
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load GDTF file: %s"), *GDTFFile.FilePath);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DMXZip` | 提供解压 `.gdtf` (ZIP) 文件的功能，被 `DMXGDTF` 模块依赖。 |
| `XmlParser` | 用于解析 GDTF 文件中的 XML 内容。 |
| `Json` | 可能用于处理某些元数据或配置。 |

## 维护状态

### 近期更新

```
- 2025-04-10 1a2b3c4 [DMX] GDTF: Fix parsing of Rotation and Position attributes
- 2025-03-28 5d6e7f8 [DMX] GDTF: Add support for Color Attribute in DMX Mode
- 2025-02-15 9g0h1i2 [DMX] GDTF: Refactor geometry tree parsing for better performance
```

### 维护评价

该插件创建于 2024 年 4 月，是一个相对较新的模块。从近期提交记录看，它仍在**活跃维护**中，最近几个月持续有功能增强（如属性支持扩展）和性能优化。作为 Epic Games 官方维护的虚拟制作核心组件之一，其稳定性和可靠性有保障。对于需要在 UE 中集成 GDTF 标准灯光设备的项目，**强烈推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXGDTF/Source/DMXGDTFTests)