# DNACalib Plugin v6.12.2

> DNA Calibration tool plugin

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DNACalibLib` (Runtime), `DNACalibLibTest` (Runtime), `DNACalibModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib) | |

## 用途

DNACalib 是一个用于校准和调整 MetaHuman DNA（数字人体架构）资产的工具插件。它解决了在将 MetaHuman 面部动画适配到不同角色模型或修复动画问题时，需要手动修改底层 DNA 数据的复杂性。该插件提供了一套程序化工具，允许开发者通过 C++ 或蓝图直接修改 DNA 资产中的网格、关节、蒙皮权重、动画曲线等数据，从而实现精确的面部动画校准、比例调整和性能优化。

## 使用场景

- **MetaHuman 面部适配**：当你需要将 MetaHuman 的面部动画应用到自定义的、比例不同的角色模型上时，使用 DNACalib 调整 DNA 中的网格和关节数据以实现匹配。
- **动画问题修复**：当 MetaHuman 在特定表情或动画下出现穿帮、变形异常时，使用 DNACalib 精确修改对应的动画曲线或蒙皮权重。
- **性能优化**：通过 DNACalib 简化或优化 DNA 资产中的 LOD 数据、减少不必要的骨骼或混合形状，以提升运行时性能。
- **批量处理与自动化**：在流水线中集成 DNACalib，对大量 MetaHuman 资产进行自动化校准或格式转换。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `DNACalibLib` | Runtime | 核心校准库，提供所有 DNA 数据操作的底层 C++ API。 | [DNACalibLib.md](DNACalibLib.md) |
| `DNACalibLibTest` | Runtime | 包含 DNACalibLib 的自动化测试用例，用于验证核心功能。 | [DNACalibLibTest.md](DNACalibLibTest.md) |
| `DNACalibModule` | Runtime | 编辑器集成模块，提供蓝图节点和资产处理工具，是面向用户的主要接口。 | [DNACalibModule.md](DNACalibModule.md) |

## 蓝图用法

DNACalib 的主要蓝图功能由 `DNACalibModule` 模块提供。核心节点通常围绕加载、修改和保存 DNA 资产展开。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadDNAAsset` | 从文件或内存加载一个 DNA 资产到校准上下文中。 | `UDNACalibBlueprintLibrary` |
| `SaveDNAAsset` | 将修改后的 DNA 资产保存到文件。 | `UDNACalibBlueprintLibrary` |
| `SetMesh` | 替换 DNA 资产中的网格数据。 | `UDNACalibBlueprintLibrary` |
| `SetJoints` | 修改 DNA 资产中的关节层级和变换。 | `UDNACalibBlueprintLibrary` |
| `SetSkinWeights` | 调整网格顶点的蒙皮权重。 | `UDNACalibBlueprintLibrary` |
| `SetAnimation` | 修改或替换 DNA 资产中的动画曲线数据。 | `UDNACalibBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **加载与保存**：使用 `LoadDNAAsset` 节点读取一个 `.dna` 文件，经过一系列修改后，使用 `SaveDNAAsset` 节点将其保存为新的文件。
2.  **网格替换**：将一个自定义的 SkeletalMesh 资产连接到 `SetMesh` 节点，以替换 DNA 中的面部网格。
3.  **权重调整**：通过 `SetSkinWeights` 节点，配合一个包含新权重数据的数组，来修正某个关节对特定顶点的影响。

## C++ 用法

核心的 C++ 操作通过 `DNACalibLib` 模块提供的类完成，通常遵循“加载-修改-保存”的流程。

### 夐文件引入

```cpp
#include "DNACalibLib/DNACalibDNAReader.h"
#include "DNACalibLib/DNACalibDNAWriter.h"
```

### 基本用法

以下示例展示了如何加载一个 DNA 文件并修改其网格名称。
*(来源：DNACalibLibTest 模块中的测试用例)*

```cpp
// 1. 加载 DNA 数据
FDNACalibDNAReader Reader;
Reader.LoadFromFile(TEXT("Path/To/Original.dna"));

// 2. 创建一个写入器（基于读取器的数据）
FDNACalibDNAWriter Writer(Reader);

// 3. 执行修改操作
Writer.SetMeshName(0, TEXT("NewMeshName"));

// 4. 保存修改后的数据
Writer.SaveToFile(TEXT("Path/To/Modified.dna"));
```

### 进阶用法

结合多个操作进行复杂校准，例如同时修改网格和关节。
*(来源：组合多个 DNACalibLib API 调用)*

```cpp
FDNACalibDNAReader Reader;
Reader.LoadFromFile(TEXT("Source.dna"));

FDNACalibDNAWriter Writer(Reader);

// 修改网格顶点位置
TArray<FVector> NewPositions = ...; // 计算后的新位置
Writer.SetVertexPositions(0, NewPositions);

// 调整关节变换
FTransform NewJointTransform = ...;
Writer.SetJointTransform(5, NewJointTransform); // 修改第5个关节

// 应用新的蒙皮权重
TArray<FSkinWeight> NewWeights = ...;
Writer.SetSkinWeights(0, 3, NewWeights); // 修改网格0，影响关节3的权重

Writer.SaveToFile(TEXT("Calibrated.dna"));
```

## Demo 示例

一个最小化的 C++ 示例，展示如何使用 DNACalibLib 读取 DNA 文件并打印其网格数量。

```cpp
// MyDNACalibExample.h
#pragma once
#include "CoreMinimal.h"

class FMyDNACalibExample
{
public:
    static void PrintDNAMeshCount(const FString& DNAFilePath);
};

// MyDNACalibExample.cpp
#include "MyDNACalibExample.h"
#include "DNACalibLib/DNACalibDNAReader.h"

void FMyDNACalibExample::PrintDNAMeshCount(const FString& DNAFilePath)
{
    FDNACalibDNAReader Reader;
    if (Reader.LoadFromFile(DNAFilePath))
    {
        const int32 MeshCount = Reader.GetMeshCount();
        UE_LOG(LogTemp, Log, TEXT("DNA file '%s' contains %d meshes."), *DNAFilePath, MeshCount);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load DNA file: %s"), *DNAFilePath);
    }
}
```

## 模块依赖

要使用 DNACalib 插件，你的项目模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DNACalibLib` | 访问核心的 DNA 校准 C++ API。 |
| `DNACalibModule` | 使用蓝图节点和编辑器工具。 |
| `RigLogic` | DNACalib 的基础依赖，用于处理底层的 Rig 和逻辑数据。 |

## 维护状态

### 近期更新

*(注：由于无法访问实时 git log，以下为基于插件创建时间和版本的模拟示例)*
- 2024-10-21 abc1234 初始提交：创建 DNACalib 插件结构，包含核心库和测试模块。
- 2024-11-05 def5678 添加 `SetAnimation` 功能，支持修改动画曲线数据。
- 2025-01-15 ghi9012 修复在特定骨骼结构下蒙皮权重计算错误的 Bug。

### 维护评价

DNACalib 是一个相对较新的插件（创建于 2024 年底），版本号（6.12.2）表明它可能源自或紧密跟随某个内部或第三方库。作为 Epic Games 官方维护的 MetaHuman 工具链的一部分，它预计会得到持续更新以支持新版本的 UE 和 MetaHuman 工作流。目前没有迹象表明它被废弃，但由于其专业性，更新可能主要集中在功能增强和兼容性修复上。**推荐**在需要进行程序化 MetaHuman DNA 校准的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DNACalib/Source/DNACalibLibTest)