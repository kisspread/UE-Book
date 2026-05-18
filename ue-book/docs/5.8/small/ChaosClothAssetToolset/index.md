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

该插件为 UE5 的 AI Agent 工具集系统提供布料资产操作能力，允许 AI Agent 通过结构化指令创建、转换和分配 ChaosClothAsset 到骨骼网格体。

核心解决的问题是：将旧版布料资产（`UClothingAssetCommon`）自动迁移到新版 `UChaosClothAsset` 格式，并完成与骨骼网格体的绑定。这是一套面向 AI 工作流的自动化工具，复制了手动在 SkeletalMesh 编辑器视口右键菜单中执行的操作。

**注意**：此插件依赖 `ToolsetRegistry`（AI Agent 工具注册表）插件，是 AI 自动化布料工作流的一部分，而非普通用户直接使用的编辑器工具。

## 使用场景

- 你有大量旧版 `UClothingAssetCommon` 布料资产需要迁移到 ChaosClothAsset 新格式
- 你需要通过 AI Agent 脚本自动化布料资产的创建、转换和 LOD 绑定
- 你需要批量将 ChaosClothAsset / Outfit Asset 绑定到骨骼网格体的特定 LOD 和 Section

## 蓝图用法

该插件的函数通过 `UFUNCTION(meta=(AICallable))` 暴露给 AI Agent 系统，而非传统的 BlueprintCallable。这些函数为静态方法，主要通过 AI 工具调用接口访问。

### 核心节点

| 函数 | 说明 | 所在类 |
|---|---|---|
| `CreateClothingAsset` | 从 ChaosClothAsset 创建布料资产并添加到骨骼网格体 | `UChaosClothAssetToolset` |
| `AssignClothingToSection` | 将布料资产绑定到骨骼网格体的指定 LOD/Section | `UChaosClothAssetToolset` |
| `ListClothingAssets` | 列出骨骼网格体上所有布料资产信息 | `UChaosClothAssetToolset` |
| `ConvertClothingAssetCommonToChaosClothAsset` | 将旧版 UClothingAssetCommon 转换为 ChaosClothAsset | `UChaosClothAssetToolset` |
| `RemoveClothingFromSection` | 从指定 Section 解除布料绑定 | `UChaosClothAssetToolset` |

### 返回数据结构

| 结构体 | 说明 |
|---|---|
| `FClothingAssetInfo` | 布料资产信息，包含 `AssetName`、`bRequiresMatchingLodIndex`、`NumClothingLods` |

### Agent 技能工作流

插件内置了一个 `UChaosClothAssetConversionSkill`，为 AI Agent 提供了完整的端到端转换指令：

1. 调用 `ListClothingAssets` 查找 `bRequiresMatchingLodIndex == false` 的旧版资产
2. 对每个旧版资产调用 `ConvertClothingAssetCommonToChaosClothAsset` 进行转换
3. 转换后的 `UChaosClothAsset` 内嵌 Dataflow 图，源资产由 `ClothingAssetImport` 节点引用
4. 调用 `CreateClothingAsset` 将新资产附加到骨骼网格体
5. 调用 `AssignClothingToSection` 逐个绑定到 LOD/Section
6. 验证通过后可调用 `RemoveClothingFromSection` 解除旧绑定

## C++ 用法

### 头文件引入

```cpp
#include "ChaosClothAsset/ClothAssetToolset.h"
```

### 基本用法

创建布料资产并绑定到骨骼网格体：

```cpp
// 从 ChaosClothAsset 创建布料资产并附加到骨骼网格体
TArray<FString> CreatedAssets = UChaosClothAssetToolset::CreateClothingAsset(
    TEXT("/Game/Characters/MyCharacter.SKEL_MyCharacter"),
    TEXT("/Game/Cloth/MyClothAsset.MyClothAsset")
);

// 将布料资产绑定到 LOD 0 的 Section 0
bool bSuccess = UChaosClothAssetToolset::AssignClothingToSection(
    TEXT("/Game/Characters/MyCharacter.SKEL_MyCharacter"),
    CreatedAssets[0],
    0,  // LodIndex
    0,  // SectionIndex
    0   // ClothingLodIndex (ChaosClothAsset 需与 LodIndex 相同)
);
```

*来源：Source/ChaosClothAssetToolset/Private/ChaosClothAsset/ClothAssetToolset.h*

### 进阶用法

自定义 AI Agent Skill 扩展布料工作流：

```cpp
UCLASS()
class UMyCustomClothSkill : public UAgentSkill
{
    GENERATED_BODY()
public:
    UMyCustomClothSkill()
    {
        Description = TEXT("Custom cloth asset workflow.");
        Toolsets.Add(UChaosClothAssetToolset::StaticClass());
        Instructions = TEXT("1. List all clothing assets...\n2. Convert legacy assets...");
    }
};
```

*来源：Source/ChaosClothAssetToolset/Private/ChaosClothAsset/ChaosClothAssetConversionSkill.h*

## Demo 示例

### 自定义 Agent Skill

```cpp
// MyClothAgentSkill.h
#pragma once

#include "ChaosClothAsset/ClothAssetToolset.h"
#include "ToolsetRegistry/AgentSkill.h"
#include "MyClothAgentSkill.generated.h"

UCLASS()
class UMyClothAgentSkill : public UAgentSkill
{
    GENERATED_BODY()

public:
    UMyClothAgentSkill()
    {
        Description = TEXT("Batch convert legacy cloth assets to ChaosClothAsset format.");
        Toolsets.Add(UChaosClothAssetToolset::StaticClass());
        Instructions = TEXT(
            "For each skeletal mesh:\n"
            "1. List clothing assets and filter legacy ones.\n"
            "2. Convert each legacy asset to ChaosClothAsset.\n"
            "3. Bind converted assets to matching LOD/Section."
        );
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | AI Agent 工具注册表和 Skill 基础设施 |
| `ChaosClothAsset` | ChaosClothAsset 核心类型和资产定义 |
| `ChaosClothAssetDataflowNodes` | 布料资产的 Dataflow 节点支持（转换时生成 Dataflow 图） |

## 维护状态

### 近期更新

```
- 2026-05-14 e9598355 Chaos Cloth Asset toolset and updated converter from legacy SKM cloth to Chaos Cloth Asset.
```

### 维护评价

- **创建时间**：2026-05-14，全新插件
- **更新频率**：仅有 1 次初始提交，尚无后续更新
- **维护状态**：🆕 刚刚创建的实验性插件，功能仍在早期阶段
- **注意事项**：
  - 标记为 `IsExperimentalVersion=true`，API 可能发生重大变化
  - 默认未启用（`EnabledByDefault=false`），需手动在插件设置中启用
  - 仅编辑器可用（`EditorOnly=true`），不会包含在打包构建中
  - 代码文件仅 4 个，功能范围较窄
- **推荐程度**：仅推荐用于实验性 AI Agent 布料工作流探索，生产环境暂不建议依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ChaosClothAssetToolset)