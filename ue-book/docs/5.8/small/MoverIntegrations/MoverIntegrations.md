# Mover Integrations

> Mover Integrations is a Unreal Engine plugin acting as an umbrella to cover a variety of modules supporting Mover's integration with other plugins, such as animation, AI, and other gameplay systems.

| 属性 | 值 |
|---|---|
| 中文名 | Mover 集成中心 |
| 分类 | Other |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（Runtime 模块） |
| 模块 | `MoverIntegrations` (Runtime), `MoverMassIntegration` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverIntegrations) | |

## 用途

该插件本身（`MoverIntegrations` 模块）是一个**结构容器**，其核心作用是为 `Mover` 系统与其他引擎或游戏系统的集成提供一个统一的、组织化的插件框架。它并不包含具体的功能逻辑，而是作为 `MoverMassIntegration` 等更具体集成模块的宿主。

其解决的问题是：`Mover` 是一个独立的、底层的运动控制系统，需要与游戏世界的其他系统（如动画蓝图、AI 行为树、大规模实体管理等）进行交互。此插件为这些特定的集成提供了一个规范化的存放位置和结构。

## 使用场景

- 你需要在一个大规模世界中，使用 `Mover` 控制成千上万个实体（如 NPC、载具）的运动，并希望利用 `Mass Entity` 系统进行高效管理 → 你需要 `MoverMassIntegration` 模块。
- 你计划为 `Mover` 创建与特定动画系统或 AI 系统的集成模块，并希望遵循 Epic 官方的结构实践 → 你应该将新模块添加到此插件中。

## 蓝图用法

### 核心节点

当前 `MoverIntegrations` 插件的核心模块（`MoverIntegrations`）**没有暴露任何蓝图节点**。它是一个纯粹的模块接口容器。

具体的蓝图功能由其子集成模块（如 `MoverMassIntegration`）提供。如果其他集成模块（如未来的动画集成）添加了蓝图函数，将会在各自的文档中说明。

## C++ 用法

### 头文件引入

要使用或扩展 `MoverIntegrations` 插件框架，你需要包含其模块头文件。

```cpp
#include "MoverIntegrations.h"
```

### 基本用法

`MoverIntegrations` 模块本身在 C++ 层面没有运行时 API。它的 `StartupModule` 和 `ShutdownModule` 是空实现。它的主要价值在于**项目组织和编译依赖管理**。

一个典型的使用模式是：在你的游戏模块的 `.Build.cs` 文件中，依赖具体的集成模块，例如 `MoverMassIntegration`。

```cpp
// 你的模块的 Build.cs 文件中
PublicDependencyModuleNames.AddRange(new string[] {
    "Mover", // 核心Mover模块
    "MoverMassIntegration", // 具体的集成模块
    // ... 其他依赖
});
```

### 进阶用法

开发者可以向此插件添加新的集成模块。这涉及创建一个新的 Runtime 模块（例如 `MoverAnimIntegration`），并在 `MoverIntegrations.uplugin` 文件的 `Modules` 数组中注册它。这保持了集成生态的整洁。

## Demo 示例

由于 `MoverIntegrations` 核心模块本身没有功能，一个有意义的演示是展示如何集成 `Mover` 和 `Mass`。以下是一个简化的、在 Actor 中设置 `MoverComponent` 并使其与 `Mass` 实体交互的示例（假设 `MoverMassIntegration` 模块已提供相关工具类）。

**MyMovingActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyMovingActor.generated.h"

class UMoverComponent;
class UMoverMassTranslatorComponent;

UCLASS()
class AMyMovingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMovingActor();

    // 核心移动组件
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UMoverComponent> MoverComponent;

    // Mass集成组件（来自MoverMassIntegration模块）
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UMoverMassTranslatorComponent> MassTranslatorComponent;
};
```

**MyMovingActor.cpp**
```cpp
#include "MyMovingActor.h"
#include "MoverComponent.h"
#include "MoverMassTranslatorComponent.h" // 来自MoverMassIntegration

AMyMovingActor::AMyMovingActor()
{
    // 创建Mover组件
    MoverComponent = CreateDefaultSubobject<UMoverComponent>(TEXT("MoverComp"));

    // 创建Mass转译器组件，它将Mover的状态与Mass实体同步
    // 这是MoverMassIntegration模块提供的关键类
    MassTranslatorComponent = CreateDefaultSubobject<UMoverMassTranslatorComponent>(TEXT("MassTranslator"));
}
```

## 模块依赖

**`MoverIntegrations` 模块**：
无特殊依赖（仅标准 Core/Engine/Slate 等）。

**`MoverMassIntegration` 模块**（其依赖至关重要）：
该模块的依赖反映了它作为桥梁的作用。

| 模块 | 用途 |
|---|---|
| `MassEntity` | UE5 大规模实体框架的核心模块 |
| `MassMovement` | Mass框架中与移动相关的组件和处理器 |
| `Mover` | 核心的Mover运动系统模块 |
| `MassSpawner` | 提供Mass实体生成功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c61e2782` | [Mass] Add Mover input-component bridge to MoverMassIntegration plugin | 为MoverMassIntegration添加了与输入组件的桥接功能 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 从MassEntity中提取出MassCore模块，可能涉及依赖调整 |
| 2025-06-10 | `675fd5ae` | CIS issue#936427: Compile errors in EngineRuntimeTests.h, MoverMassTranslators.h and MoverMassTransl... | 修复了编译错误，属于维护性修复 |
| 2025-05-07 | `1207fa81` | Mover: Adding UE5 Mover-Mass translators along with a Mover Integrations plugin... | 插件及核心Mover-Mass转译器的初始提交 |

### 维护评价

- **创建时间**：不到一年，是一个相对较新的插件。
- **更新频率**：创建以来有持续的功能性更新（Mass输入桥接）和基础架构调整（MassCore模块化），最近一次更新在2026年5月，表明仍在**活跃维护**中。
- **状态**：作为官方实验性功能的一部分，其集成模块（如MoverMassIntegration）正在积极开发和完善。
- **建议**：推荐在新项目中尝试使用 `MoverMassIntegration`，尤其是涉及大规模实体模拟的场景。注意关注其依赖的 `MassEntity` 等模块的稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MoverIntegrations)
- [官方文档]()：暂无
- [测试用例]()：暂未发现专门的测试文件目录，集成测试可能包含在 `Mover` 或 `Mass` 模块的测试中。