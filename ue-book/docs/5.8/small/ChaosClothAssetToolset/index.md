# ChaosClothAsset Toolset

> AI agent tools for creating and assigning ChaosClothAsset clothing to skeletal meshes.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产工具集 |
| 分类 | Cloth |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosClothAssetToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ChaosClothAssetToolset) | |

## 用途

该插件是一个 **AI 代理（Agent）工具集**，提供一套通过字符串路径操作骨骼网格体上布料资产的 API。它的核心价值在于：

1. **程序化布料管理**：无需打开 SkeletalMesh 编辑器，即可通过代码/AI 代理完成布料资产的创建、绑定、解绑和查询操作
2. **旧版布料迁移**：将基于 `UClothingAssetCommon` 的旧版布料资产（通过 `UChaosClothingSimulationFactory` 创建）自动转换为新的 `UChaosClothAsset` 格式，转换过程中保留配置数据和权重贴图
3. **对接 ToolsetRegistry 系统**：作为 `UToolsetDefinition` 子类，向 UE 的 AI 代理框架注册可调用的工具函数，使 AI 能够自主完成布料资产的管理流程

简而言之：这是为 **AI 驱动的自动化工作流** 设计的布料资产操作接口，复刻了 SkeletalMesh 编辑器视口右键菜单中"应用布料数据"/"移除布料数据"的功能。

## 使用场景

- 你需要通过 AI 代理自动为角色骨骼网格体创建和绑定 ChaosClothAsset 布料 → 使用此插件
- 你有大量角色的旧版布料资产需要迁移到新 ChaosClothAsset 格式 → 使用 `ConvertClothingAssetCommonToChaosClothAsset`
- 你需要在自动化管线中批量管理骨骼网格体的布料绑定关系 → 使用 `CreateClothingAsset` / `AssignClothingToSection`
- 你正在开发 AI 代理系统，需要让 AI 理解并操作布料工作流 → 参考 `UChaosClothAssetConversionSkill` 中的指令模板

## 蓝图用法

所有函数均标记为 `meta=(AICallable)`，属于 AI 代理可调用的工具函数。函数全部为 `static`，无需实例化。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateClothingAsset` | 从 ChaosCloth/Outfit 资产创建布料资产并添加到骨骼网格体的布料数组 | `UChaosClothAssetToolset` |
| `AssignClothingToSection` | 将布料资产绑定到指定 LOD 和 Section | `UChaosClothAssetToolset` |
| `RemoveClothingFromSection` | 从指定 LOD Section 解除布料绑定 | `UChaosClothAssetToolset` |
| `ListClothingAssets` | 列出骨骼网格体上所有布料资产信息 | `UChaosClothAssetToolset` |
| `GetSectionClothing` | 查询指定 Section 绑定的布料资产名称 | `UChaosClothAssetToolset` |
| `ConvertClothingAssetCommonToChaosClothAsset` | 将旧版 UClothingAssetCommon 转换为新的 UChaosClothAsset | `UChaosClothAssetToolset` |

### 数据结构

| 结构体 | 说明 |
|---|---|
| `FClothingAssetInfo` | 布料资产信息，包含 `AssetName`、`bRequiresMatchingLodIndex`、`NumClothingLods` |

### 使用示例

**基本工作流 — 查询并绑定布料：**

1. 调用 `ListClothingAssets` 获取骨骼网格体上所有布料资产
2. 从返回的 `FClothingAssetInfo` 数组中选择目标资产
3. 调用 `AssignClothingToSection` 将布料绑定到目标 LOD/Section
4. 如果是 ChaosClothAsset 类型（`bRequiresMatchingLodIndex == true`），`ClothingLodIndex` 必须与 `LodIndex` 相同

**迁移工作流 — 旧版布料转新格式：**

1. 调用 `ListClothingAssets`，找到 `bRequiresMatchingLodIndex == false` 的条目（即旧版 UClothingAssetCommon）
2. 调用 `ConvertClothingAssetCommonToChaosClothAsset` 进行转换
3. 调用 `CreateClothingAsset` 将新资产附加到网格体
4. 调用 `AssignClothingToSection` 绑定新布料（`ClothingLodIndex` = `LodIndex`）
5. 验证无误后，调用 `RemoveClothingFromSection` 移除旧版绑定

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothAssetToolset.h"
```

### 基本用法

列出骨骼网格体上的布料资产并查询绑定信息：

```cpp
// 列出目标骨骼网格体上的所有布料资产
TArray<FClothingAssetInfo> Assets = UChaosClothAssetToolset::ListClothingAssets(
    TEXT("/Game/Characters/SM_Character"));

for (const FClothingAssetInfo& Info : Assets)
{
    UE_LOG(LogTemp, Log, TEXT("布料资产: %s, LOD数: %d, 需匹配LOD: %s"),
        *Info.AssetName,
        Info.NumClothingLods,
        Info.bRequiresMatchingLodIndex ? TEXT("是") : TEXT("否"));
}

// 查询特定 Section 的布料绑定
FString BoundCloth = UChaosClothAssetToolset::GetSectionClothing(
    TEXT("/Game/Characters/SM_Character"),
    /*LodIndex=*/ 0,
    /*SectionIndex=*/ 2);

if (!BoundCloth.IsEmpty())
{
    UE_LOG(LogTemp, Log, TEXT("Section 2 绑定了布料: %s"), *BoundCloth);
}
```

### 进阶用法

完整的旧版布料迁移流程（对应 `UChaosClothAssetConversionSkill` 中描述的工作流）：

```cpp
const FString SkeletalMeshPath = TEXT("/Game/Characters/SM_Character");
const FString OutputFolder = TEXT("/Game/Cloth/");

// 1. 列出所有布料资产，查找旧版类型
TArray<FClothingAssetInfo> Assets = UChaosClothAssetToolset::ListClothingAssets(SkeletalMeshPath);

for (const FClothingAssetInfo& Info : Assets)
{
    if (Info.bRequiresMatchingLodIndex)
    {
        continue; // 跳过已是 ChaosClothAsset 类型的
    }

    // 2. 转换旧版布料资产为新的 ChaosClothAsset
    FString NewAssetPath = UChaosClothAssetToolset::ConvertClothingAssetCommonToChaosClothAsset(
        SkeletalMeshPath,
        Info.AssetName,
        OutputFolder,
        /*AssetName=*/ TEXT("")); // 空字符串使用默认名 "CA_Converted_<source>"

    if (NewAssetPath.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("转换失败: %s"), *Info.AssetName);
        continue;
    }

    // 3. 将新资产附加到骨骼网格体
    TArray<FString> CreatedAssets = UChaosClothAssetToolset::CreateClothingAsset(
        SkeletalMeshPath, NewAssetPath);

    if (CreatedAssets.Num() > 0)
    {
        // 4. 绑定到 LOD 0, Section 0
        // ChaosClothAsset 类型的 ClothingLodIndex 必须与 LodIndex 相同
        UChaosClothAssetToolset::AssignClothingToSection(
            SkeletalMeshPath,
            CreatedAssets[0],
            /*LodIndex=*/ 0,
            /*SectionIndex=*/ 0,
            /*ClothingLodIndex=*/ 0); // 与 LodIndex 相同

        // 5. 移除旧版布料绑定
        UChaosClothAssetToolset::RemoveClothingFromSection(
            SkeletalMeshPath,
            /*LodIndex=*/ 0,
            /*SectionIndex=*/ 0);
    }
}
```

## Demo 示例

以下展示如何创建一个自定义的编辑器命令，利用工具集批量处理场景中所有角色的布料迁移：

```cpp
// ClothMigrationCommandlet.h
#pragma once

#include "Commandlets/Commandlet.h"
#include "ClothMigrationCommandlet.generated.h"

UCLASS()
class UClothMigrationCommandlet : public UCommandlet
{
    GENERATED_BODY()

public:
    virtual int32 Main(const FString& Params) override;
};
```

```cpp
// ClothMigrationCommandlet.cpp
#include "ClothMigrationCommandlet.h"
#include "ChaosClothAsset/ClothAssetToolset.h"

int32 UClothMigrationCommandlet::Main(const FString& Params)
{
    const FString MeshPath = TEXT("/Game/Characters/SM_Hero");
    const FString OutputFolder = TEXT("/Game/Cloth/Migrated/");

    // 列出布料资产
    TArray<FClothingAssetInfo> Assets = UChaosClothAssetToolset::ListClothingAssets(MeshPath);

    UE_LOG(LogTemp, Display, TEXT("找到 %d 个布料资产"), Assets.Num());

    int32 ConvertedCount = 0;

    for (const FClothingAssetInfo& Info : Assets)
    {
        if (Info.bRequiresMatchingLodIndex)
        {
            UE_LOG(LogTemp, Display, TEXT("跳过已是新版格式: %s"), *Info.AssetName);
            continue;
        }

        FString NewPath = UChaosClothAssetToolset::ConvertClothingAssetCommonToChaosClothAsset(
            MeshPath, Info.AssetName, OutputFolder, TEXT(""));

        if (NewPath.IsEmpty())
        {
            UE_LOG(LogTemp, Error, TEXT("转换失败: %s"), *Info.AssetName);
            continue;
        }

        TArray<FString> Created = UChaosClothAssetToolset::CreateClothingAsset(MeshPath, NewPath);

        if (Created.Num() > 0)
        {
            UChaosClothAssetToolset::AssignClothingToSection(
                MeshPath, Created[0], 0, 0, 0);
            UChaosClothAssetToolset::RemoveClothingFromSection(MeshPath, 0, 0);
            ConvertedCount++;
        }
    }

    UE_LOG(LogTemp, Display, TEXT("成功迁移 %d 个布料资产"), ConvertedCount);
    return 0;
}
```

## 模块依赖

Build.cs 中仅有 `Core` 依赖，但 .uplugin 声明了以下插件依赖：

| 插件 | 用途 |
|---|---|
| `ToolsetRegistry` | AI 代理工具集注册框架，提供 `UToolsetDefinition` 基类 |
| `ChaosClothAsset` | ChaosClothAsset 布料资产核心实现 |
| `ChaosClothAssetDataflowNodes` | ChaosClothAsset 的 Dataflow 节点，转换过程中用于构建新资产的 Dataflow 图 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `e9598355` | Chaos Cloth Asset toolset and updated converter from legacy SKM cloth to Chaos Cloth Asset. | 插件首次创建，包含完整的布料工具集和旧版布料转换器 |

### 维护评价

- **创建时间**：2026-05-14，非常新的插件
- **实验性**：`.uplugin` 中 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明仍处于早期实验阶段
- **代码规模**：仅 4 个源文件，功能聚焦且精简
- **依赖关系**：依赖 `ChaosClothAsset` 和 `ToolsetRegistry` 等实验性插件，整个链条尚不稳定
- **仅一次提交**：目前只有一条初始提交记录，尚无后续迭代
- **⚠️ 警告**：这是实验性的 AI 代理工具，API 随时可能发生破坏性变更。仅建议在实验性项目中使用，不建议用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ChaosClothAssetToolset)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)
- [ChaosClothAsset 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosClothAsset)