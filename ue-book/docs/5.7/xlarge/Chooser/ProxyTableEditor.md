# Chooser

> Use Chooser and Proxy Tables to build dynamic asset selection logic.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `Chooser` (Runtime), `ChooserEditor` (Editor), `ChooserUncooked` (UncookedOnly), `ProxyTable` (Runtime), `ProxyTableEditor` (Editor), `ProxyTableUncooked` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2022-05-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser) | |

## 用途

Chooser 是一个**数据驱动的动态资产选择系统**，专为动画管线设计，但其通用架构适用于任何需要基于上下文条件动态选择资产的场景。

该插件解决的核心问题是：**在运行时根据多个输入参数（GameplayTag、对象属性、枚举值等）从一组候选资产中选择最匹配的那一个**。

传统做法中，动画选择逻辑通常硬编码在蓝图或 C++ 中（大量 Branch/Switch 节点），导致：
- 逻辑分散难以维护
- 添加新动画需要修改代码
- 策划无法独立调整选择规则

Chooser 通过**表格化配置**解决这些问题——将选择规则定义为数据资产（Chooser Table），美术和策划可以在编辑器中可视化地配置选择逻辑，无需程序员介入。

插件包含两个互补的子系统：

1. **Chooser Table**：定义"输入条件 → 输出资产"的映射规则表。支持多列条件组合、通配符匹配、优先级排序。
2. **Proxy Table**：资产代理/间接引用层。通过代理表引用资产，可以在不修改引用者的情况下替换实际资产，支持基于上下文的动态解析。

两者结合使用时，Chooser Table 负责"选择哪个资产"，Proxy Table 负责"资产的实际解析和替换"。

## 使用场景

- 你在做一个角色动画系统，需要根据角色状态（站立/奔跑/跳跃）+ 武器类型（剑/枪/空手）+ 地形（平地/斜坡）动态选择动画 → 用 Chooser Table 定义多维条件映射
- 你需要为不同角色种族（人类/精灵/兽人）使用不同的动画集，但不想为每个种族单独配置蓝图 → 用 Proxy Table 做资产代理，运行时根据种族解析到不同动画
- 你想让策划在编辑器中可视化地配置动画选择规则，而不是让程序员写 Switch 语句 → Chooser Table 提供表格化的可视化编辑界面
- 你需要在不修改已有蓝图引用的情况下，批量替换某个角色的所有动画资产 → 通过 Proxy Table 的间接引用实现
- 你在做模块化角色系统，不同装备组合需要不同的动画蒙太奇 → Chooser Table 的多列条件匹配天然适合这种场景

## 蓝图用法

> ⚠️ 本插件默认未启用（`EnabledByDefault: false`），需在 Project Settings → Plugins 中手动启用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EvaluateChooser` | 根据输入上下文评估 Chooser Table，返回选中的资产 | `UChooserTable` |
| `GetProxyTableResult` | 通过 Proxy Table 解析代理引用，返回实际资产 | `UProxyTable` |
| `SetChooserContext` | 设置 Chooser 评估时的上下文对象 | `UChooserFunctionLibrary` |

### 使用示例（蓝图描述）

**基本 Chooser Table 评估流程：**

1. 创建一个 Chooser Table 数据资产（Content Browser → Miscellaneous → Chooser Table）
2. 在 Chooser Table 编辑器中配置列（输入条件）和行（候选资产）
3. 在蓝图中，使用 `EvaluateChooser` 节点，传入 Chooser Table 引用和当前上下文对象
4. 节点输出选中的资产对象，可直接连接到 Play Animation 等节点

**Proxy Table 使用流程：**

1. 创建 Proxy Table 数据资产
2. 在 Proxy Table 中配置代理条目，每个条目关联一个逻辑名称和实际资产
3. 在蓝图中通过 Proxy Table 引用资产，而非直接引用
4. 运行时，Proxy Table 根据上下文解析到正确的实际资产

## C++ 用法

### 头文件引入

```cpp
#include "Chooser.h"
#include "ChooserTable.h"
#include "ProxyTable.h"
```

### 基本用法

```cpp
// 评估 Chooser Table 获取选中的资产
// 来源: Engine/Plugins/Chooser/Source/Chooser/

UChooserTable* ChooserTable = LoadObject<UChooserTable>(nullptr, TEXT("/Game/Data/DT_AnimChooser"));
UObject* Context = GetCharacter(); // 上下文对象，通常是角色实例

if (ChooserTable)
{
    UObject* SelectedAsset = ChooserTable->Evaluate(Context);
    if (UAnimMontage* Montage = Cast<UAnimMontage>(SelectedAsset))
    {
        PlayAnimMontage(Montage);
    }
}
```

### 进阶用法

```cpp
// 使用 Proxy Table 进行动态资产解析
// Proxy Table 允许在不修改引用的情况下替换实际资产

UProxyTable* ProxyTable = LoadObject<UProxyTable>(nullptr, TEXT("/Game/Data/PT_CharacterAnims"));

if (ProxyTable)
{
    // 通过代理名称获取实际资产
    FProxyTableResult Result;
    ProxyTable->FindProxy(Context, ProxyName, Result);
    
    if (UObject* ResolvedAsset = Result.GetObject())
    {
        // 使用解析后的资产
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | Chooser Table 的条件列支持 GameplayTag 匹配 |
| `GameplayTagsEditor` | 编辑器中 GameplayTag 选择器的 UI 支持 |
| `PropertyEditor` | 自定义属性面板和 Chooser Table 编辑器 |
| `AssetDefinition` | 资产类型定义和 Content Browser 集成 |

## 子模块文档

本插件规模较大（339 个源文件），按功能拆分为以下子模块：

| 子模块 | 类型 | 说明 |
|---|---|---|
| [Chooser](./Chooser.md) | Runtime | Chooser Table 核心运行时逻辑 |
| [ChooserEditor](./ChooserEditor.md) | Editor | Chooser Table 编辑器 UI 和资产工厂 |
| [ChooserUncooked](./ChooserUncooked.md) | UncookedOnly | Chooser Table 的未打包阶段处理 |
| [ProxyTable](./ProxyTable.md) | Runtime | Proxy Table 核心运行时逻辑 |
| [ProxyTableEditor](./ProxyTableEditor.md) | Editor | Proxy Table 编辑器 UI 和资产工厂 |
| [ProxyTableUncooked](./ProxyTableUncooked.md) | UncookedOnly | Proxy Table 的未打包阶段处理 |

## 维护状态

### 近期更新

```
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 79c5eb28e881 Proxy Table Editor Crash fixes
- c9d7ba02cba0 Fix broken icons on ProxyTable asset types
```

- 第一条是 Epic 批量代码优化，添加内联生成宏以减少编译时间
- 第二条修复了 Proxy Table 编辑器的崩溃问题，说明编辑器稳定性仍在改进
- 第三条修复了 ProxyTable 资产类型图标显示问题，属于 UI polish

### 维护评价

- **创建时间**：2022 年 5 月，相对较新的插件
- **活跃度**：近期有实质性 bug 修复和代码优化，属于**活跃维护**状态
- **启用状态**：`EnabledByDefault: false`，说明 Epic 仍将其视为可选功能，尚未默认集成到所有项目
- **推荐度**：✅ 推荐使用。对于需要复杂动画选择逻辑的项目，Chooser Table 比硬编码的 Switch/Branch 更易维护。Proxy Table 的间接引用模式也有利于资产管理和热替换。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser)
- [官方文档]()（暂无）

---

# ProxyTableEditor

> Proxy Table 编辑器模块，提供 Proxy Table 资产的编辑器 UI、自定义属性面板和资产工厂。

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | ProxyTableEditor |
| 类型 | Editor |
| 路径 | `Engine/Plugins/Chooser/Source/ProxyTableEditor/` |

## 用途

ProxyTableEditor 是 Proxy Table 的编辑器支持模块，负责：

1. **资产工厂**：在 Content Browser 中创建新的 Proxy Table 数据资产
2. **自定义编辑器**：提供 Proxy Table 的专用编辑界面，可视化配置代理条目
3. **属性自定义**：在 Details 面板中为 Proxy Table 相关属性提供自定义 UI
4. **资产类型定义**：注册 Proxy Table 资产类型，使其在 Content Browser 中正确显示图标和操作菜单

## 近期更新

```
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 79c5eb28e881 Proxy Table Editor Crash fixes
- c9d7ba02cba0 Fix broken icons on ProxyTable asset types
```

- 崩溃修复和图标修复表明该模块仍在积极维护中
- 批量代码优化说明 Epic 在持续改进代码质量

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ProxyTable` | Proxy Table 核心运行时类型定义 |
| `Chooser` | Chooser 核心模块，与 Chooser Table 共享基础设施 |
| `UnrealEd` | 编辑器框架 |
| `PropertyEditor` | 自定义属性面板 |
| `AssetDefinition` | 资产类型注册 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Chooser/Source/ProxyTableEditor)