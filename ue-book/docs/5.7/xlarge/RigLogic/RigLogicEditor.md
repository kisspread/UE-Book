# RigLogic Plugin v10.3.0

> RigLogic Plugin for Facial Animation v10.3.0

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（DNA资产、导入UI） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 插件是一个用于处理和驱动角色面部动画的高级系统。它并非简单的动画播放器，而是一个完整的**DNA（数字核酸）数据处理管线**。其核心功能是将外部工具（如 MetaHuman Creator）生成的 `.dna` 文件导入到 Unreal Engine 中，并将其数据附加到 `USkeletalMesh` 上。这些 DNA 数据包含了驱动角色面部骨骼、变形目标（Morph Targets）和蒙皮权重所需的复杂逻辑，能够实现极其逼真和可控的面部动画效果。

该插件解决了将高保真数字人角色资产无缝集成到 UE5 工作流中的关键问题，是 MetaHuman 框架的核心技术支撑之一。

## 使用场景

- **影视与虚拟制片**：需要创建和驱动照片级真实感数字人角色的项目。
- **游戏开发**：为游戏角色创建高度复杂和可控的面部动画系统，超越传统的骨骼动画和 BlendShape。
- **数字人应用**：开发虚拟主播、客服或任何需要实时、高保真面部动画的应用程序。
- **资产管线**：作为从 DCC 工具（如 Maya）到 UE5 的数字人资产导入和更新流程的核心环节。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Import Skeletal Mesh DNA File` | 将指定的 DNA 文件导入并应用到目标骨骼网格体资产上。 | `UDNAImporterLibrary` |
| `Reset To Default` | 将 DNA 资产导入 UI 的选项重置为默认值。 | `UDNAAssetImportUI` |

### 使用示例（蓝图描述）

1.  **基本导入**：
    *   在蓝图中，使用 `Import Skeletal Mesh DNA File` 节点。
    *   将 DNA 文件的完整路径连接到 `FileName` 引脚。
    *   将目标 `USkeletalMesh` 资产（例如，一个已经绑好基础骨骼的 MetaHuman 网格体）连接到 `Mesh` 引脚。
    *   执行该节点，DNA 数据将被解析并应用到网格体上，驱动其面部骨骼和变形目标。

2.  **自定义导入选项**：
    *   在导入前，可以创建一个 `UDNAAssetImportUI` 对象。
    *   设置其 `SkeletalMesh` 属性来指定要导入到的网格体（留空则会新建）。
    *   调用其 `Reset To Default` 节点来重置选项（如果需要）。
    *   然后将此 UI 对象传递给底层的导入工厂逻辑（通常通过编辑器菜单触发，蓝图直接调用较少）。

## C++ 用法

### 头文件引入

```cpp
#include "DNAImporterLibrary.h"
#include "DNAAssetImportUI.h"
#include "DNAImporter.h"
```

### 基本用法

从 `UDNAImporterLibrary` 的蓝图函数可以推断出最基本的 C++ 调用方式。

```cpp
// 假设你已经有一个 USkeletalMesh* 指针 MeshToImportTo
// 和一个 DNA 文件路径 FString DNADirectory = TEXT(“C:/Characters/MyMetaHuman.dna”);

// 调用静态函数导入 DNA
UDNAImporterLibrary::ImportSkeletalMeshDNA(DNADirectory, MeshToImportTo);
```

### 进阶用法

对于需要更精细控制导入过程（如批处理、自动化管线）的场景，可以使用 `FDNAImporter` 单例。

```cpp
// 获取导入器单例
FDNAImporter* Importer = FDNAImporter::GetInstance();
if (Importer)
{
    // 获取并配置导入选项
    FDNAAssetImportOptions* Options = Importer->GetImportOptions();
    if (Options)
    {
        Options->bCanShowDialog = false; // 禁用导入对话框，用于自动化
        Options->SkeletalMesh = MySkeletalMesh; // 指定目标网格体
    }

    // 设置 DNA 文件名
    Importer->SetDNAFileName(TEXT(“C:/Characters/AnotherCharacter.dna”));

    // 注意：实际的导入执行通常由编辑器工厂（UDNAAssetImportFactory）触发，
    // 直接调用 FDNAImporter 的方法可能不完整。更常见的用法是通过编辑器扩展。
}

// 使用完毕后，考虑清理单例（通常在插件关闭时）
// FDNAImporter::DeleteInstance();
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在编辑器工具或命令中触发 DNA 导入。

**MyDNAImportTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyDNAImportTool
{
public:
    static void ImportDNAToMesh(const FString& DNAFilePath, USkeletalMesh* TargetMesh);
};
```

**MyDNAImportTool.cpp**
```cpp
#include "MyDNAImportTool.h"
#include "DNAImporterLibrary.h"
#include "Engine/SkeletalMesh.h"

void FMyDNAImportTool::ImportDNAToMesh(const FString& DNAFilePath, USkeletalMesh* TargetMesh)
{
    if (!TargetMesh)
    {
        UE_LOG(LogTemp, Error, TEXT("Target Skeletal Mesh is null."));
        return;
    }

    if (!FPaths::FileExists(DNAFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("DNA file not found: %s"), *DNAFilePath);
        return;
    }

    // 调用核心导入函数
    UDNAImporterLibrary::ImportSkeletalMeshDNA(DNAFilePath, TargetMesh);
    UE_LOG(LogTemp, Log, TEXT("DNA import initiated for %s"), *DNAFilePath);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数，用于处理导入的网格体数据。 |
| `RHI`, `RenderCore` | 可能用于处理与渲染相关的资源或数据转换（如纹理、材质参数）。 |
| `MessageLog` | 用于在编辑器中向用户显示导入过程中的警告和错误信息。 |

## 维护状态

### 近期更新

- `a1c904daea63` [RigLogicEditor] Fixed bug related to SKM selection for DNA import and some small improvements to DNA Importing process
- `a2e75189887d` Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup using LyraEditor win64 development as target)
- `2057280165b3` Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n

### 维护评价

- **创建时间**：2020年7月，作为 MetaHuman 技术栈的一部分，相对较新。
- **最近更新**：最近的提交（`a1c904daea63`）是针对 DNA 导入流程的**功能性 Bug 修复和改进**，表明该插件仍在被积极使用和维护。
- **维护状态**：**维护中**。作为 Epic 官方数字人解决方案的核心组件，预计会持续更新以支持新版本的 UE 和 MetaHuman 工具链。
- **已知限制**：该插件高度依赖于特定的 DNA 文件格式和外部工具链。直接使用需要理解其数据管线。
- **推荐使用**：**强烈推荐**用于任何涉及高保真数字人角色的项目。它是目前 UE5 中处理复杂面部动画的工业标准方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)
- [官方文档]() (暂无独立文档，通常作为 MetaHuman 文档的一部分)
- [测试用例]() (测试代码位于 `RigLogicLibTest` 模块)