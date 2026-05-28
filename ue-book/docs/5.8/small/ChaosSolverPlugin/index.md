# Chaos Solver

> Physics Solver（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 混沌求解器 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（代码资产） |
| 模块 | `ChaosSolverEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-12-12 |
| 年龄标签 | 🆕（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosSolverPlugin) | |

## 用途

该插件为 **Chaos 物理系统**提供了一个可在编辑器中创建和管理的**物理求解器资产** (`UChaosSolver`)。它作为 Epic 的 Chaos 物理框架在编辑器端的配置和管理入口，允许用户通过资产化的方式创建、配置和驱动独立的物理模拟世界。

其主要解决的问题是：将 Chaos 物理系统的核心配置（如求解器参数）从游戏逻辑或场景组件中解耦，使其成为一个可被引擎内容浏览器管理、可序列化、可重复使用的资产对象。这使得物理世界的设置和复用变得更加灵活和直观。

## 使用场景

- 当你需要**在同一个关卡中运行多个独立的、配置不同的物理模拟**时（例如，一个用于主世界，另一个用于特效或特定对象的局部模拟），可以使用多个 Chaos Solver 资产来分别驱动。
- 当你希望**将物理求解器的复杂配置（如迭代次数、精度、重力等）保存为独立资产**，以便在不同场景或项目中快速复用和调优时。
- 作为 Chaos 物理系统开发者，你需要一个**在编辑器端管理物理求解器生命周期和属性的标准化接口**时。

## 蓝图用法

该插件主要在编辑器端工作，提供的核心功能是资产的创建和管理。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Chaos Solver` | 通过编辑器工厂创建一个新的 `UChaosSolver` 资产。 | `UChaosSolverFactory` |

### 使用示例（蓝图描述）

在编辑器中，你通常通过以下方式使用该插件：

1.  在内容浏览器的空白处**右键**。
2.  在右键菜单中找到 **Physics -> Chaos** 子菜单（由 `UAssetDefinition_ChaosSolver` 提供分类）。
3.  选择 **Chaos Solver** 来创建一个新的求解器资产。
4.  双击打开该资产，在其细节面板中配置物理模拟参数。
5.  在场景中的组件或游戏逻辑中，引用该资产以启动并驱动对应的物理模拟。

该插件还提供了物理调试控制面板 (`FChaosDebugSubstepControlCustomization`)，你可以在游戏或场景的细节面板中找到相关的暂停、步进等调试按钮，用于精细化的物理模拟调试。

## C++ 用法

该插件主要为编辑器服务，C++ 用法侧重于创建和管理 `UChaosSolver` 资产。

### 头文件引入

```cpp
#include "Chaos/ChaosSolverFactory.h"
```

### 基本用法

通过工厂类在代码中程序化创建 `UChaosSolver` 资产。
（来源：`ChaosSolverFactory.h`）

```cpp
// 创建一个新的 ChaosSolver 资产
UClass* SolverClass = UChaosSolver::StaticClass();
UObject* Outer = GetTransientPackage(); // 或其他合适的 Outer
FName Name = TEXT("MyCustomSolver");
EObjectFlags Flags = RF_Public | RF_Standalone;
UChaosSolver* NewSolver = UChaosSolverFactory::StaticFactoryCreateNew(
    SolverClass, Outer, Name, Flags, nullptr, GWarn);
if (NewSolver)
{
    // 资产创建成功，可以进一步配置属性
    // NewSolver->SomeProperty = Value;
}
```

### 进阶用法

结合模块接口 (`IChaosSolverEditorPlugin`) 在编辑器模块中进行更精细的控制。

```cpp
// 确保编辑器插件模块可用
if (IChaosSolverEditorPlugin::IsAvailable())
{
    // 获取插件实例，可用于管理控制台命令等
    IChaosSolverEditorPlugin& SolverPlugin = IChaosSolverEditorPlugin::Get();
    // ... 插件特定的操作
}
```

## Demo 示例

这是一个最小化的示例，展示如何在编辑器工具代码中创建 ChaosSolver 资产。

**ChaosSolverDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FChaosSolverDemo
{
public:
    static UChaosSolver* CreateSolverAsset();
};
```

**ChaosSolverDemo.cpp**
```cpp
#include "ChaosSolverDemo.h"
#include "Chaos/ChaosSolver.h"
#include "Chaos/ChaosSolverFactory.h"

UChaosSolver* FChaosSolverDemo::CreateSolverAsset()
{
    UClass* SolverClass = UChaosSolver::StaticClass();
    // 使用游戏模块作为资产的 Outer，或根据上下文选择合适对象
    UPackage* OuterPackage = CreatePackage(nullptr, TEXT("/Game/MySolvers"));
    FName UniqueName = MakeUniqueObjectName(OuterPackage, SolverClass, TEXT("DemoSolver"));
    EObjectFlags Flags = RF_Public | RF_Standalone | RF_Transactional;

    UChaosSolver* Solver = UChaosSolverFactory::StaticFactoryCreateNew(
        SolverClass, OuterPackage, UniqueName, Flags, nullptr, GWarn);

    if (Solver)
    {
        // 配置并保存资产
        Solver->MarkPackageDirty();
        FAssetRegistryModule::AssetCreated(Solver);
    }
    return Solver;
}
```

## 模块依赖

该插件的 `Build.cs` 文件未在源码分析中提供。根据其公开头文件中引用的类型推断，使用者的模块**可能**需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `ChaosSolvers` | 提供核心的 `UChaosSolver` 类定义 |
| `ChaosSolverEngine` | 将求解器资产与引擎运行时物理世界连接 |

（注：以上依赖为基于代码内容的推测。具体依赖需查阅 `ChaosSolverEditor.Build.cs` 文件。插件本身仅包含 `ChaosSolverEditor` 模块。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `0d40a411` | [ContentBrowser] New Add Menu Physics Menu | 调整了内容浏览器右键菜单的Physics子菜单结构。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了可能导致重复符号的链接错误。 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 更新了头文件，修正了DLL导出宏的声明位置。 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 移除了旧的、已废弃的头文件包含顺序宏。 |
| 2023-11-15 | `b64f2e25` | [Deprecation Cleanup] Remove deprecated code in actor factory class | 清理了Actor工厂类中的废弃代码。 |

### 维护评价

- **活跃状态**：插件自2018年创建，最近一次提交（2026-04-14）表明它仍在被维护和集成到最新的编辑器功能中。
- **维护性质**：近期更新以**底层维护和兼容性修复**为主（链接错误、代码规范、废弃清理），而非功能性增强。
- **实验性标记**：尽管标记为 `Beta` 并且位于 `Experimental` 目录下，但其基础功能似乎已稳定多年。
- **总结**：这是一个相对稳定但功能聚焦的基础插件，为Chaos物理系统提供编辑器端的资产化管理。它不经常需要更新，但仍在积极维护以确保与引擎的兼容性。对于需要使用Chaos物理求解器资产的项目，它是可用且推荐的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosSolverPlugin)
- [官方文档]()（暂无）