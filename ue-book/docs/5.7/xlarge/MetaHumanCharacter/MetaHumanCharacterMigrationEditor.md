# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、角色资产） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

---

## 用途

MetaHuman Character 插件是 Epic Games 为 UE5 打造的**MetaHuman 角色资产创建与编辑系统**。它解决的核心问题是：如何在引擎内完成 MetaHuman 角色的创建、编辑、调色板管理和版本迁移，而无需依赖外部 MetaHuman Creator 工具。

该插件包含 7 个模块，覆盖从运行时核心逻辑到编辑器 UI 的完整工作流：

| 模块 | 职责 |
|---|---|
| **MetaHumanCharacter** | 核心运行时模块，定义角色资产数据结构和基础逻辑 |
| **MetaHumanCharacterEditor** | 编辑器模块，提供角色创建/编辑的 UI 和工具 |
| **MetaHumanCharacterPalette** | 调色板系统，管理角色外观组件（发型、服装等）的资产库 |
| **MetaHumanCharacterPaletteEditor** | 调色板编辑器，提供调色板资产的编辑 UI |
| **MetaHumanCharacterMigrationEditor** | 迁移编辑器，处理旧版 MetaHuman 角色资产的版本迁移 |
| **MetaHumanDefaultPipeline** | 默认运行时管线，定义角色的默认处理流程 |
| **MetaHumanDefaultEditorPipeline** | 默认编辑器管线，定义编辑器中的默认处理流程 |

**注意**：此插件标记为 `IsBetaVersion=true` 且 `EnabledByDefault=false`，需要手动在插件管理器中启用。

---

## 使用场景

- 你需要在 UE5 编辑器中**创建和编辑 MetaHuman 角色**，而不依赖外部 MetaHuman Creator 云服务
- 你需要管理 MetaHuman 角色的**外观调色板**（发型、面部毛发、服装等组件的组合）
- 你需要将**旧版 MetaHuman 角色资产迁移到新版格式**（从早期 MetaHuman 插件升级）
- 你需要自定义 MetaHuman 角色的**处理管线**（Pipeline），例如添加自定义的 LOD 生成或渲染步骤

---

## 蓝图用法

由于此插件主要面向编辑器工作流，大部分 API 为 C++ 层面。运行时模块提供有限的蓝图接口用于角色数据访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 获取角色资产 | 获取 MetaHuman 角色资产引用 | `UMetaHumanCharacter` |
| 获取调色板 | 获取角色关联的外观调色板 | `UMetaHumanCharacterPalette` |

> **注意**：此插件的核心功能主要通过编辑器 UI 和 C++ API 使用，蓝图接口有限。详细 API 请参考 C++ 用法章节。

---

## C++ 用法

### 头文件引入

```cpp
// 核心角色模块
#include "MetaHumanCharacter.h"

// 调色板模块
#include "MetaHumanCharacterPalette.h"

// 迁移模块（如需程序化迁移）
#include "MetaHumanCharacterMigrationEditor.h"
```

### 基本用法

MetaHuman Character 插件的核心是角色资产（`UMetaHumanCharacter`）和调色板资产（`UMetaHumanCharacterPalette`）的管理。以下为基本操作模式：

```cpp
// 加载一个 MetaHuman 角色资产
UMetaHumanCharacter* Character = LoadObject<UMetaHumanCharacter>(
    nullptr, TEXT("/Game/MetaHumans/MyCharacter.MyCharacter")
);

if (Character)
{
    // 获取角色关联的调色板
    UMetaHumanCharacterPalette* Palette = Character->GetPalette();
    
    // 访问角色的基本属性
    // 具体属性取决于版本和管线实现
}
```

### 进阶用法：迁移旧版资产

`MetaHumanCharacterMigrationEditor` 模块专门处理旧版 MetaHuman 角色资产的迁移。当用户从早期版本的 MetaHuman 插件升级时，需要将旧格式资产转换为新格式：

```cpp
// 迁移流程通常通过编辑器 UI 触发
// 程序化迁移需要使用 MigrationEditor 模块的 API
// 注意：迁移过程中会处理骨骼适配、材质映射等复杂逻辑
```

**迁移模块的典型工作流**：
1. 检测项目中的旧版 MetaHuman 角色资产
2. 分析资产结构差异（骨骼、材质、LOD 等）
3. 执行数据转换和适配
4. 生成新版格式的角色资产

---

## Demo 示例

由于此插件为编辑器工具型插件，主要通过编辑器 UI 使用。以下为最小化的 C++ 集成示例：

```cpp
// MyMetaHumanManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyMetaHumanManager.generated.h"

class UMetaHumanCharacter;
class UMetaHumanCharacterPalette;

UCLASS()
class UMyMetaHumanManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    // 加载并验证 MetaHuman 角色
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    UMetaHumanCharacter* LoadMetaHumanCharacter(const FSoftObjectPath& AssetPath);

    // 获取角色的调色板信息
    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    UMetaHumanCharacterPalette* GetCharacterPalette(UMetaHumanCharacter* Character);
};
```

```cpp
// MyMetaHumanManager.cpp
#include "MyMetaHumanManager.h"
#include "MetaHumanCharacter.h"
#include "MetaHumanCharacterPalette.h"

UMetaHumanCharacter* UMyMetaHumanManager::LoadMetaHumanCharacter(const FSoftObjectPath& AssetPath)
{
    UMetaHumanCharacter* Character = Cast<UMetaHumanCharacter>(AssetPath.TryLoad());
    
    if (!Character)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load MetaHuman Character: %s"), *AssetPath.ToString());
    }
    
    return Character;
}

UMetaHumanCharacterPalette* UMyMetaHumanManager::GetCharacterPalette(UMetaHumanCharacter* Character)
{
    if (!Character)
    {
        return nullptr;
    }
    
    return Character->GetPalette();
}
```

---

## 模块依赖

由于此插件包含 7 个模块且为 MetaHuman 生态系统的一部分，依赖关系较为复杂。以下是各模块的关键依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 核心角色数据结构和逻辑 |
| `MetaHumanCharacterPalette` | 调色板资产系统 |
| `MetaHumanCoreTech` | MetaHuman 核心技术库（骨骼、网格处理） |
| `MetaHumanCoreTechLib` | MetaHuman 核心技术底层库 |
| `RigLogic` | 面部绑定逻辑引擎 |
| `MeshDescription` | 网格数据描述和处理 |
| `SkeletalMeshDescription` | 骨骼网格描述 |
| `GeometryCore` | 几何处理核心库 |
| `MeshConversion` | 网格格式转换 |

> **注意**：具体依赖因模块而异。使用迁移模块（`MetaHumanCharacterMigrationEditor`）时，还需要依赖编辑器相关模块。

---

## 维护状态

### 近期更新

```
- 6deab153e70b [UEMHC] Remove unused adapt neck option #rb filip.micic
- b35afec6a307 [UEMHC] Fix for Arabic localization issues
- 3add5cc33bce [UEMHC] Fix ensure when migrating MetaHuman
```

### 维护评价

**综合评价：活跃维护中，但为 Beta 状态**

- **创建时间**：2025-03-17，非常新的插件
- **更新频率**：近期有多次提交，包括功能清理（移除未使用选项）、本地化修复（阿拉伯语）和迁移 bug 修复
- **维护状态**：活跃维护中，Epic Games 团队持续开发
- **Beta 状态**：标记为 `IsBetaVersion=true`，API 和功能可能发生变化
- **启用状态**：`EnabledByDefault=false`，需要手动启用

**推荐程度**：
- ✅ 如果你需要在引擎内创建/编辑 MetaHuman 角色，这是官方推荐的工具
- ⚠️ 由于是 Beta 版本，生产环境使用需谨慎，建议关注版本更新
- ⚠️ 迁移模块（MigrationEditor）专门用于处理旧版资产升级，如果你是新项目可能不需要

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [官方文档]()（暂无）
- [测试用例]()（待确认）

---

# MetaHuman Character Migration Editor 模块文档

> 本模块为 MetaHuman Character 插件的迁移编辑器子模块，专门处理旧版 MetaHuman 角色资产的版本迁移。

| 属性 | 值 |
|---|---|
| 模块名 | MetaHumanCharacterMigrationEditor |
| 模块类型 | Runtime |
| 所属插件 | MetaHumanCharacter |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 0 年） |

## 模块用途

`MetaHumanCharacterMigrationEditor` 模块负责将旧版本的 MetaHuman 角色资产迁移到新格式。当 MetaHuman 插件的资产格式发生重大变更时，此模块提供自动化的迁移工具，确保用户的现有资产能够平滑升级。

### 典型使用场景

- 从 MetaHuman 插件早期版本升级到当前版本
- 项目中存在旧格式的 MetaHuman 角色资产需要转换
- 批量迁移多个 MetaHuman 角色资产

## 近期更新

```
- 6deab153e70b [UEMHC] Remove unused adapt neck option #rb filip.micic
- b35afec6a307 [UEMHC] Fix for Arabic localization issues
- 3add5cc33bce [UEMHC] Fix ensure when migrating MetaHuman
```

**更新解读**：
1. **移除未使用的颈部适配选项**：代码清理，移除了迁移过程中不再需要的 `adapt neck` 选项
2. **修复阿拉伯语本地化问题**：解决了迁移 UI 中阿拉伯语显示的问题
3. **修复迁移时的 ensure 断言**：修复了在迁移 MetaHuman 角色时触发的 `ensure` 断言错误，提高了迁移稳定性

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 核心角色数据结构 |
| `MetaHumanCharacterEditor` | 编辑器基础功能 |
| `MetaHumanCharacterPalette` | 调色板系统（迁移时需要处理外观数据） |

## 使用注意事项

1. **迁移前备份**：建议在执行批量迁移前备份项目
2. **Beta 状态**：此模块随主插件标记为 Beta，迁移逻辑可能随版本更新
3. **不可逆操作**：迁移通常会修改资产格式，建议先在测试分支上验证