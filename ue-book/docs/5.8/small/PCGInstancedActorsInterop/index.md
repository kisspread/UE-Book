# Procedural Content Generation Framework (PCG) Instanced Actors Interop

> Extra plugin for Procedural Content Generation Framework interacting with Instanced Actors plugin.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | PCG 实例化角色互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `PCGInstancedActorsInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGInstancedActorsInterop) | |

## 用途

这个插件是PCG（程序化内容生成框架）与“实例化角色”（Instanced Actors）插件之间的桥梁。它的核心作用是**让PCG图能够生成“实例化角色”类型的Actor**。

**Instanced Actors插件**旨在通过将大量相似的静态网格体实例合并为一个优化的渲染实体，来高效渲染大量重复物体（如树木、岩石、建筑部件）。**PCG插件**则用于程序化地生成场景内容。

在没有这个互操作插件时，PCG图通常会生成常规的静态网格体Actor或使用层级实例化静态网格体（HISM）。**PCGInstancedActorsInterop** 提供了一个专用的PCG节点，允许用户将PCG的生成流程直接与Instanced Actors的优化渲染系统对接，从而在需要极致渲染性能的大规模程序化生成场景中获得优势。

**重要限制（源自代码注释）**：
*   某些Actor类必须在项目设置中预先注册（参见Instanced Actors文档）。
*   不支持在运行时动态创建或移除实例化角色。
*   不支持PCG的“预览”和“加载为预览”工作流。

## 使用场景

*   **开放世界环境生成**：使用PCG程序化生成海量树木、植被、岩石等自然物体，并通过此插件将其作为Instanced Actors生成，以获得最佳的渲染性能。
*   **大规模城市/建筑生成**：程序化生成重复性高的建筑外墙、窗户、栅栏等元素，利用Instanced Actors减少绘制调用。
*   **需要极致优化的场景**：当场景中存在数万乃至数十万个相似几何体实例，且HISM方案仍不能满足性能要求时，可尝试使用此插件与Instanced Actors结合。

## 蓝图用法

此插件主要提供一个新的PCG节点，其行为通过 `UPCGSpawnInstancedActorsSettings` 类的属性进行配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Instanced Actors` | 一个PCG生成节点，将输入的点数据转化为Instanced Actors。 | `UPCGSpawnInstancedActorsSettings` |

### 使用示例（蓝图描述）

1.  **创建PCG图**：在内容浏览器中新建一个PCG图资产。
2.  **添加节点**：在图中添加一个`Spawn Instanced Actors`节点（在PCG节点搜索中可找到）。
3.  **配置属性**：
    *   **指定Actor类**：在节点的细节面板中，如果不勾选 `bSpawnByAttribute`，则可以在 `ActorClass` 属性中选择一个在Instanced Actors中注册好的Actor类（例如一个已配置好的树木蓝图）。
    *   **按属性生成**：如果勾选 `bSpawnByAttribute`，则可以通过 `SpawnAttributeSelector` 指定输入数据中的某个属性（例如一个软类路径属性）来决定每个点要生成的Actor类。
    *   **静默空类警告**：如果输入数据中可能包含无效的Actor类，勾选 `bMuteOnEmptyClass` 可以避免在日志中输出大量警告。
4.  **连接输入**：将PCG图中上游生成点数据的节点（如Surface Sampler, Grid Sampler等）连接到此节点的输入引脚。
5.  **执行生成**：运行PCG图，节点会根据配置在每个输入点位置生成对应的Instanced Actor实例。

## C++ 用法

此插件主要通过蓝图PCG节点使用。C++层面主要是模块声明和资源管理，直接编程使用较少。

### 头文件引入

```cpp
#include "PCGInstancedActorsInteropModule.h"
#include "Elements/PCGSpawnInstancedActors.h"
```

### 基本用法

在C++中，你通常不会直接实例化 `FPCGSpawnInstancedActorsElement`，因为它是通过 `UPCGSpawnInstancedActorsSettings` 的蓝图节点自动创建的。但你可以通过 `UPCGSpawnInstancedActorsSettings` 的C++类来了解其属性。

```cpp
// 获取或创建一个PCG Spawn Instanced Actors节点的设置对象 (通常在自定义PCG节点工具中)
UPCGSpawnInstancedActorsSettings* SpawnSettings = NewObject<UPCGSpawnInstancedActorsSettings>();
SpawnSettings->bSpawnByAttribute = false;
SpawnSettings->ActorClass = AMyInstancedTree::StaticClass(); // 设置要生成的Actor类
SpawnSettings->bMuteOnEmptyClass = true;
```

**注意**：`ExecuteInternal` 方法是 `FPCGSpawnInstancedActorsElement` 的内部实现，用于执行实际的生成逻辑，它要求只能在主线程执行（`CanExecuteOnlyOnMainThread` 返回 `true`），且不可缓存（`IsCacheable` 返回 `false`）。

### 进阶用法

此插件提供的资源类 `UPCGInstancedActorsManagedResource` 用于管理生成的Instanced Actors句柄（`Handles`数组）。它继承自 `UPCGManagedResource`，处理了资源的释放、移动和编辑器状态转换。如果你需要编写自定义逻辑来操作由PCG生成的Instanced Actors的句柄，可以研究此类。

## Demo 示例

一个展示如何在C++中引用此模块的最小示例。

**MyGameModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyGameModule.cpp**
```cpp
#include "MyGameModule.h"
#include "PCGInstancedActorsInteropModule.h" // 引入PCG Instanced Actors互操作模块的头文件

#define LOCTEXT_NAMESPACE "FMyGameModule"

void FMyGameModule::StartupModule()
{
    // 模块启动逻辑
    // 可以在这里检查PCGInstancedActorsInterop模块是否加载
    if (FModuleManager::Get().IsModuleLoaded("PCGInstancedActorsInterop"))
    {
        UE_LOG(LogTemp, Log, TEXT("PCGInstancedActorsInterop module is loaded."));
    }
}

void FMyGameModule::ShutdownModule()
{
    // 模块关闭逻辑
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_PRIMARY_GAME_MODULE(FMyGameModule, MyGame, "MyGame");
```

## 模块依赖

要使用此插件提供的PCG节点，你的项目需要启用以下插件（这是插件级别的依赖）：

| 插件 | 用途 |
|---|---|
| `PCG` | 程序化内容生成框架，本插件的基础。 |
| `InstancedActors` | 实例化角色插件，本插件生成的目标类型。 |

对于`PCGInstancedActorsInterop`模块本身，其Build.cs的详细依赖未在提供信息中列出。根据其头文件内容（使用了UPCGSettings, UPCGManagedResource等PCG类型），它至少依赖于`PCG`模块。通常，这类互操作插件的依赖在UpLugin的`Plugins`部分已经声明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到新的UE_LOGF宏。 |
| 2025-11-11 | `587881cc` | [PCG] Refactored clear pcg link/ moving resource method to be a bit more flexible and more futurepro | 重构了清除PCG链接和移动资源的方法，使其更灵活、更具前瞻性。 |
| 2025-10-21 | `0cb1be6a` | [PCG] Reviewed what nodes support base point data & also control flow nodes that support gpu proxy d | 审查了支持基础点数据的节点，以及支持GPU代理的控制流节点。 |
| 2025-08-27 | `74386d31` | Fixup API macro usage | 修复了API宏的使用问题。 |
| 2025-06-13 | `d35afb72` | [PCG] Adjusted the instanced actor resources so that they can't be released at runtime, which preven | 调整了实例化角色资源，防止在运行时释放，从而避免相关崩溃。 |

### 维护评价

*   **状态**：**维护中**。该插件创建于2025年4月，最近一次更新是2026年4月，表明仍在接受维护。
*   **更新内容**：近期的更新主要是底层框架的适配（如日志宏迁移）、资源管理逻辑的优化和重构，以及兼容性改进。这些是维护性更新，表明团队在关注其稳定性，但没有重大新功能。
*   **已知限制**：插件本身明确标注了运行时不支持创建/移除、不支持预览等限制，这源于底层Instanced Actors插件的特性。
*   **推荐度**：**适用于特定优化需求**。如果你需要在程序化生成中极致优化大量静态物体的渲染性能，并且可以接受其限制（主要是运行时静态），那么这是一个值得尝试的实验性工具。但由于它是实验性的（`IsExperimentalVersion=true`）且默认未启用，不建议在核心生产环境中过度依赖，应持续关注官方对Instanced Actors和PCG互操作支持的后续发展。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGInstancedActorsInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/) (PCG框架通用文档)
- 测试用例：此插件目录下未发现独立的测试文件。相关的功能测试可能位于PCG或Instanced Actors插件的测试目录中。