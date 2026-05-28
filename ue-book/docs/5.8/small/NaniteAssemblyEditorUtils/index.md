# Nanite Assembly Editor Utilities

> Experimental support for Nanite Assembly creation in blueprint.

| 属性 | 值 |
|---|---|
| 中文名 | Nanite 组装编辑器工具 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产示例） |
| 模块 | `NaniteAssemblyEditorUtils` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteAssemblyEditorUtils) | |

## 用途

该插件提供了一套蓝图接口，用于**程序化地创建和编辑 Nanite Assembly 静态网格体与骨骼网格体资产**。Nanite Assembly 允许将多个静态网格体或骨骼网格体组合成一个单一的网格体资产，以利用 Nanite 的渲染性能优势。此插件将这一流程封装为蓝图节点，使开发者无需通过编辑器手动操作即可在运行时或编辑器脚本中批量、精确地构建复杂的组装体。

## 使用场景

- 你需要在编辑器脚本或蓝图中，根据一系列规则或外部数据，将多个静态网格体（如建筑模块、机械零件）程序化组合成一个高效的 Nanite Assembly 资产。
- 你需要为游戏角色创建基于骨骼的组装装备（如盔甲、武器），并将多个部件绑定到同一骨架的不同骨骼上，生成一个完整的 Nanite Assembly 骨骼网格体。
- 你需要动态修改已存在的 Nanite Assembly 资产的构成部件。

## 蓝图用法

该插件的核心是 `UNaniteAssemblyBuilder` 的两个具体实现类，它们提供了从创建到完成构建的全流程蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Begin New Static Mesh Assembly Build` | 开始构建一个新的 Nanite Assembly 静态网格体资产。 | `UNaniteAssemblyStaticMeshBuilder` |
| `Begin Edit Static Mesh Assembly Build` | 开始编辑一个已存在的 Nanite Assembly 静态网格体。 | `UNaniteAssemblyStaticMeshBuilder` |
| `Add Assembly Part` | 向当前构建的静态网格体 Assembly 添加一个部件实例（通过变换）。 | `UNaniteAssemblyStaticMeshBuilder` |
| `Add Assembly Parts From Component` | 将一个 `UStaticMeshComponent` 及其所有实例添加到 Assembly 中。 | `UNaniteAssemblyStaticMeshBuilder` |
| `Finish Assembly Build` | 完成构建并输出最终的 Nanite Assembly 静态网格体资产。 | `UNaniteAssemblyStaticMeshBuilder` |
| `Begin New Skeletal Mesh Assembly Build` | 开始构建一个新的 Nanite Assembly 骨骼网格体资产。 | `UNaniteAssemblySkeletalMeshBuilder` |
| `Begin Edit Skeletal Mesh Assembly Build` | 开始编辑一个已存在的 Nanite Assembly 骨骼网格体。 | `UNaniteAssemblySkeletalMeshBuilder` |
| `Add Assembly Part (Skeletal)` | 向当前构建的骨骼网格体 Assembly 添加一个部件实例（通过绑定）。 | `UNaniteAssemblySkeletalMeshBuilder` |
| `Create Binding By Bone Name` | 为骨骼网格体部件创建一个基于骨骼名称的绑定。 | `UNaniteAssemblySkeletalMeshBuilder` |
| `Create Binding By Socket Name` | 为骨骼网格体部件创建一个基于插槽（Socket）名称的绑定。 | `UNaniteAssemblySkeletalMeshBuilder` |
| `Finish Assembly Build (Skeletal)` | 完成构建并输出最终的 Nanite Assembly 骨骼网格体资产。 | `UNaniteAssemblySkeletalMeshBuilder` |
| `Add Material Slot Group` | 在构建器中创建一个新的材质插槽组，用于控制材料的合并范围。 | `UNaniteAssemblyBuilder` |
| `Add Material Slot` | 向指定的材质插槽组中添加一个带材质的插槽。 | `UNaniteAssemblyBuilder` |

### 使用示例（蓝图描述）

1.  **创建静态网格体 Assembly**：
    *   使用 `Begin New Static Mesh Assembly Build` 节点，指定新资产的目标路径和名称。
    *   对于要添加的每个 `UStaticMesh`，调用 `Add Assembly Part` 节点，并传入对应的 `FTransform`。
    *   （可选）使用 `Add Material Slot Group` 和 `Add Material Slot` 配置材料合并行为。
    *   最后，调用 `Finish Assembly Build` 节点，将生成的资产输出到一个变量中。

2.  **创建骨骼网格体 Assembly**：
    *   使用 `Begin New Skeletal Mesh Assembly Build` 节点，需要提供一个基础骨骼网格体以继承其骨架。
    *   对于每个部件，先使用 `Create Binding By Bone Name` 节点为其创建绑定（指定骨骼、权重、变换）。
    *   然后，将创建好的绑定传入 `Add Assembly Part (Skeletal)` 节点。
    *   最后，调用 `Finish Assembly Build (Skeletal)` 节点完成构建。

## C++ 用法

### 头文件引入

```cpp
#include “NaniteAssemblyStaticMeshBuilder.h”
#include “NaniteAssemblySkeletalMeshBuilder.h”
```

### 基本用法

以下示例展示了如何在 C++ 中程序化创建一个新的 Nanite Assembly 静态网格体。

```cpp
// （基于头文件 API 推断的用法示例）
void CreateNaniteAssemblyProgrammatically()
{
    // 1. 准备创建参数
    FNaniteAssemblyCreateNewParameters CreateParams;
    CreateParams.TargetDirectory.Path = TEXT(“/Game/GeneratedAssemblies”);
    CreateParams.AssetName = TEXT(“MyProceduralAssembly”);
    CreateParams.bOverwriteExisting = true;

    // 2. 创建并初始化构建器
    UNaniteAssemblyStaticMeshBuilder* Builder = UNaniteAssemblyStaticMeshBuilder::BeginNewStaticMeshAssemblyBuild(CreateParams);
    if (!Builder) return;

    // 3. 准备要添加的部件和变换
    UStaticMesh* PartMeshA = LoadObject<UStaticMesh>(nullptr, TEXT(“/Game/Meshes/PartA”));
    UStaticMesh* PartMeshB = LoadObject<UStaticMesh>(nullptr, TEXT(“/Game/Meshes/PartB”));
    
    FTransform PartATransform(FRotator(0, 0, 0), FVector(100, 0, 0));
    FTransform PartBTransform(FRotator(0, 45, 0), FVector(-100, 0, 50));

    // 4. 向构建器中添加部件
    Builder->AddAssemblyPart(PartMeshA, PartATransform);
    Builder->AddAssemblyPart(PartMeshB, PartBTransform);

    // 5. 完成构建并获取结果
    UStaticMesh* FinalAssemblyMesh = nullptr;
    bool bSuccess = Builder->FinishAssemblyBuild(FinalAssemblyMesh);
    if (bSuccess && FinalAssemblyMesh)
    {
        UE_LOG(LogTemp, Log, TEXT(“Nanite Assembly created at: %s”), *FinalAssemblyMesh->GetPathName());
    }
}
```

### 进阶用法

对于骨骼网格体，需要使用绑定结构并指定骨骼信息。

```cpp
// （基于头文件 API 推断的用法示例）
void CreateSkeletalNaniteAssembly()
{
    USkeletalMesh* BaseMesh = LoadObject<USkeletalMesh>(nullptr, TEXT(“/Game/Characters/BaseCharacter”));
    UNaniteAssemblySkeletalMeshBuilder* SkelBuilder = UNaniteAssemblySkeletalMeshBuilder::BeginEditSkeletalMeshAssemblyBuild(BaseMesh);

    // 为一个部件创建骨骼绑定
    FNaniteAssemblySkeletalMeshPartBinding Binding;
    // 假设使用一个辅助函数来填充绑定
    SkelBuilder->CreateBindingByBoneName(Binding, FName(“hand_r”), 1.0f, FTransform(FVector(0,0,10)));

    UStaticMesh* WeaponMesh = LoadObject<UStaticMesh>(nullptr, TEXT(“/Game/Weapons/Sword”));
    // 注意：骨骼网格体的部件可以是静态网格体
    SkelBuilder->AddAssemblyPart(WeaponMesh, Binding);

    USkeletalMesh* OutMesh = nullptr;
    SkelBuilder->FinishAssemblyBuild(OutMesh);
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何构建一个简单的静态网格体 Nanite Assembly。

**NaniteAssemblyDemo.h**
```cpp
#pragma once
#include “CoreMinimal.h”
#include “NaniteAssemblyStaticMeshBuilder.h”

class FNaniteAssemblyDemo
{
public:
    static UNaniteAssemblyStaticMeshBuilder* CreateSimpleDemoAssembly();
};
```

**NaniteAssemblyDemo.cpp**
```cpp
#include “NaniteAssemblyDemo.h”

UNaniteAssemblyStaticMeshBuilder* FNaniteAssemblyDemo::CreateSimpleDemoAssembly()
{
    // 创建构建器
    FNaniteAssemblyCreateNewParameters Params;
    Params.TargetDirectory.Path = TEXT(“/Game/Demo/Assemblies”);
    Params.AssetName = TEXT(“SimpleCubeAssembly”);
    Params.bOverwriteExisting = true;

    UNaniteAssemblyStaticMeshBuilder* Builder = UNaniteAssemblyStaticMeshBuilder::BeginNewStaticMeshAssemblyBuild(Params);
    if (!Builder) return nullptr;

    // 假设有一个基础立方体网格体
    UStaticMesh* CubeMesh = LoadObject<UStaticMesh>(nullptr, TEXT(“/Engine/BasicShapes/Cube”));
    if (!CubeMesh) return nullptr;

    // 将同一个立方体添加两次，第二次旋转并移动
    Builder->AddAssemblyPart(CubeMesh, FTransform(FVector(200, 0, 0))); // 第一个立方体
    Builder->AddAssemblyPart(CubeMesh, FTransform(FRotator(0, 45, 0), FVector(200, 200, 0))); // 旋转后的立方体

    // 完成构建
    UStaticMesh* OutMesh = nullptr;
    Builder->FinishAssemblyBuild(OutMesh);
    return Builder;
}
```

## 模块依赖

该插件提供了一个用于编辑器/脚本的工具集，其自身模块 `NaniteAssemblyEditorUtils` 类型为 `Editor`。使用该插件时，你的模块需要依赖：

| 模块 | 用途 |
|---|---|
| `MeshDescription` | 核心网格体数据结构，用于操作和组装网格体几何数据。 |
| `MeshConversion` | 在不同网格体表示（如 `UStaticMesh` 与 `FMeshDescription`）之间转换。 |
| `Nanite` | Nanite 渲染核心模块，与 Nanite Assembly 底层数据交互。 |
| `NaniteAssemblyCore` | 提供 `FNaniteAssemblyDataBuilder` 等底层构建工具，是本插件的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，提升日志规范性和可追溯性。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了打印格式说明符，解决了潜在的输出或崩溃问题。 |
| 2025-09-16 | `2be24593` | [NaniteAssemblyBuilder] Move module header in public | 将模块头文件移至 Public 目录，方便外部模块正确引用。 |
| 2025-09-11 | `cc3f30f9` | [NaniteAssemblies] Some final cleanup of NaniteAssemblyEditorUtils and the Blueprint interfaces it e | 对插件代码和其暴露的蓝图接口进行了最终整理和清理。 |
| 2025-09-06 | `7ad5a8f5` | [NaniteAssemblies] Adding a skeletal mesh Nanite Assembly builder to the NaniteAssemblyEditorUtils p | 为插件新增了骨骼网格体 Nanite Assembly 构建器功能。 |

### 维护评价

该插件创建于 **2025 年 9 月**，非常年轻。尽管被标记为**实验性**且默认禁用，但近期的提交记录（最新至 2026 年 4 月）表明它仍在**积极维护中**，包含了功能添加（骨骼网格体支持）和代码质量改进（日志迁移、格式修复）。作为一个面向未来 Nanite 工作流的工具集，它处于早期快速迭代阶段。目前功能聚焦且稳定，适用于进行原型开发和验证 Nanite Assembly 的程序化生成工作流，但不建议用于需要长期稳定性的生产环境核心功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NaniteAssemblyEditorUtils)
- [官方文档]()（暂无）