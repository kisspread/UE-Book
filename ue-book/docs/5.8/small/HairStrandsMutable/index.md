# Mutable Groom Extensions

> Adds Mutable functionality to work with Grooms from the HairStrands plugin

| 属性 | 值 |
|---|---|
| 中文名 | 发廊可变体 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HairStrandsMutable` (Runtime), `HairStrandsMutableEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairStrandsMutable) | |

## 用途

本插件为 `Mutable` 可定制对象系统提供处理 `HairStrands` 发廊（Groom）资产的能力。它解决了 `Mutable` 系统原本无法直接实例化、管理和应用 `Groom` 资产属性的问题，使设计师能够在可定制对象中创建和管理具有可变毛发外观的角色或物体。

## 使用场景

- 你在做一个需要角色外观深度定制的游戏（如MMORPG或角色创建系统），希望玩家能改变角色的发型、发量、卷曲度等毛发属性。
- 你需要在游戏中动态生成大量外观各异的 NPC，其毛发（Groom）也需要跟随 `Mutable` 系统一起变化。

## 蓝图用法

本插件主要扩展 `Mutable` 编辑器和运行时系统的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCustomizableObjectGroomNode` | 从可定制对象中获取指定的 Groom 常量节点 | `UCustomizableObjectNodeGroomConstant` |
| `Mutable Groom Constant` | (编辑器节点) 在可定制对象蓝图中定义一个可变的 Groom 资产引用 | `UCustomizableObjectNodeGroomConstant` |

### 使用示例（蓝图描述）

1.  **在 Customizable Object 编辑器中**：使用新增的 `Groom Constant` 节点来引用一个基础 Groom 资产。该节点的输出可以连接到其他材质或网格体修改节点，从而实现 Groom 属性的变异。
2.  **在运行时游戏蓝图中**：当 `Mutable` 系统生成实例时，会根据配置自动实例化和附加相应的 `Groom` 组件到角色上。

## C++ 用法

### 头文件引入

```cpp
#include "HairStrandsMutableModule.h"
```

### 基本用法

插件运行时模块的核心功能是定义 `Groom` 在 `Mutable` 系统中的数据结构。

```cpp
// 创建一个用于存储 Groom 资产引用的扩展数据结构体
FMutableGroomExtensionData GroomData;
// 设置要应用的 Groom 资产
GroomData.GroomAsset = MyGroomAsset;
```

*（概念示例，实际使用通过 `Mutable` 蓝图节点）*

### 进阶用法

编辑器模块 `HairStrandsMutableEditor` 提供了在编辑器内操作 `Groom` 节点的功能，通常在 `Mutable` 资产编辑流程中使用。

## Demo 示例

```cpp
// MyCharacter.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "HairStrandsMutableTypes.h" // 包含 FMutableGroomExtensionData 定义
#include "MyCharacter.generated.h"

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    // 可用于存储当前实例的 Groom 扩展数据
    UPROPERTY(Transient)
    FMutableGroomExtensionData CurrentGroomData;

    // 应用 Groom 数据的函数（概念性）
    void ApplyGroomFromMutableData(const FMutableGroomExtensionData& InData);
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `HairStrands` | 提供核心 Groom 资产和组件 |
| `Mutable` | 提供核心可定制对象和实例化系统 |
| `MutableEditor` | (编辑器模块) 提供可定制对象编辑器功能 |
| `UnrealEd` | (编辑器模块) 提供编辑器基础框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `814648b2` | [mutable] Fixed check failure when trying to spawn a new object on a PostLoad call. | 修复在PostLoad调用期间尝试生成新对象时的检查失败。 |
| 2026-03-11 | `aeecf60f` | [HairStrandsMutable] Fix ensure when registgering to Movie Sequence Template actors. | 修复向影片序列模板Actor注册时的ensure断言。 |
| 2026-03-06 | `87b39b7f` | [Mutable] Fix Extension Data not being applied when an Instance is already generated. | 修复当实例已生成时扩展数据未被应用的错误。 |
| 2026-02-27 | `f8a35ec8` | [Mutable] Add support for UAssetUserData in SKM Parameter and Constants nodes. | 在骨骼网格体参数和常量节点中添加对UAssetUserData的支持。 |
| 2026-01-29 | `17d7a59b` | [Mutable] Fix PSO check with grooms. | 修复与Groom相关的PSO检查问题。 |

### 维护评价

该插件目前处于**积极维护**状态。尽管它被标记为实验性（`IsExperimentalVersion: true`）且默认未启用，但从Git历史看，其更新频率非常高，近几个月内有多次针对性的Bug修复和功能增强（如支持AssetUserData）。这表明该插件是 `Mutable` 和 `Groom` 系统集成方案的重要且活跃的实验组件。

**推荐使用**：如果你的项目深度使用 `Mutable` 系统进行角色定制，并且需要集成 `Groom`（毛发），那么此插件是必不可少的。需要注意的是，由于是实验性功能，在大型项目中使用前应进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairStrandsMutable)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/HairStrandsMutable/Tests) (如果存在)