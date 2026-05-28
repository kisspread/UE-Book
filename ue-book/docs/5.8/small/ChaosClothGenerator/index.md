# Chaos Cloth Generator

> Chaos Cloth Data Generator for ML Deformer

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料生成器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 (蓝图资产) |
| 模块 | `ChaosClothGenerator` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/ChaosClothGenerator) | |

## 用途

该插件是一个**数据生成工具**，专门用于为机器学习变形器（ML Deformer）准备训练数据。它解决的核心问题是：如何高效地为基于 Chaos 物理引擎的布料模拟生成大规模、高质量的训练数据集。

传统上，要训练一个 ML Deformer 来模拟复杂的布料动态，开发者需要：
1. 手动为各种姿势运行布料物理模拟。
2. 记录下每个姿势的最终网格形状（作为“真值”）。
3. 这个过程繁琐、耗时且容易出错。

**ChaosClothGenerator 自动化了这个过程**。用户只需配置输入（骨骼网格体、布料资产、动画序列）和输出目标，插件就能自动调用 Chaos 布料求解器，模拟动画序列中的每一帧，并将生成的网格数据保存为几何缓存（Geometry Cache）。这个缓存可以直接用作 ML Deformer 训练流程中的“目标网格”数据。

## 使用场景

- 你在使用 **ML Deformer** 框架，并希望训练一个能预测角色身上布料（如披风、裙子、衬衫）物理运动的模型。
- 你需要为训练流程生成**批量的、标准化的模拟数据**，而不是手动模拟单个动作。
- 你的动画序列包含大量不同的姿态和动作，需要一次性生成对应的布料最终状态。
- 你想**调试或检查**特定单帧的布料模拟结果，确保数据生成正确。

## 蓝图用法

该插件主要通过其编辑器界面（面板和按钮）操作，而不是通过常规的蓝图节点。其核心配置属性暴露在 `UClothGeneratorProperties` 对象中。

### 核心属性 (在生成器面板中配置)

| 属性 | 说明 | 所在类 |
|---|---|---|
| `SkeletalMeshAsset` | 用于 ML Deformer 的输入骨骼网格体。 | `UClothGeneratorProperties` |
| `ClothAsset` | 用于模拟的混沌布料资产，应与骨骼网格体不同。 | `UClothGeneratorProperties` |
| `AnimationSequence` | 包含用于生成模拟数据的训练姿势的动画序列。 | `UClothGeneratorProperties` |
| `FramesToSimulate` | 指定要模拟的帧范围（如 "0, 2, 5-10, 12-15"）。留空则模拟所有帧。 | `UClothGeneratorProperties` |
| `SimulatedCache` | 输出的几何缓存资产，存储所有模拟结果。 | `UClothGeneratorProperties` |
| `TimeStep` | 模拟的时间步长。 | `UClothGeneratorProperties` |
| `NumSteps` | 每帧的模拟迭代步数。 | `UClothGeneratorProperties` |
| `NumThreads` | 用于并行模拟的线程数。 | `UClothGeneratorProperties` |
| `bDebug` | 启用单帧调试模式。 | `UClothGeneratorProperties` |
| `DebugFrame` | 在调试模式下要检查的帧索引。 | `UClothGeneratorProperties` |
| `DebugCache` | 调试模式输出的几何缓存。 | `UClothGeneratorProperties` |

### 使用示例（在 ML Deformer 编辑器中操作）

1.  打开一个 **ML Deformer** 资产进行编辑。
2.  在编辑器工具栏中，找到由 `FChaosClothGeneratorToolsMenuExtender` 添加的 **“Chaos Cloth Generator”** 菜单/选项卡。
3.  在生成器面板中：
    - 为 `SkeletalMeshAsset` 分配你的角色骨骼网格体。
    - 为 `ClothAsset` 分配为该角色制作的 Chaos 布料资产。
    - 为 `AnimationSequence` 分配一个包含多种姿势的动画序列。
    - 设置 `FramesToSimulate`（例如，为了快速测试，可以输入 "0, 10, 50"）。
    - 为 `SimulatedCache` 指定一个新的或现有的几何缓存资产路径。
4.  调整 `Simulation Settings`（时间步长、迭代次数等）以平衡速度和精度。
5.  点击生成按钮（由插件面板提供，对应于 `EClothGeneratorActions::StartGenerate`）。
6.  插件会开始异步模拟。完成后，指定的 `SimulatedCache` 将被更新，其中包含了每一帧模拟后的布料网格顶点位置数据。

## C++ 用法

该插件是一个编辑器工具，其核心逻辑通过 `FChaosClothGenerator` 类驱动。它通常不直接在其他 C++ 项目中调用，而是作为 ML Deformer 编辑器的一部分。

### 头文件引入

```cpp
// 访问生成器属性和启动生成
#include "ChaosClothGenerator.h" // 对于 FChaosClothGenerator 类
// 访问自定义面板和菜单扩展
#include "ChaosClothGeneratorToolsMenuExtender.h"
```

### 基本用法

插件的核心流程封装在 `FChaosClothGenerator` 中，它是一个 `FTickableEditorObject`。以下代码展示了其内部工作流程的简化概念（通常不直接使用，仅供理解）。

```cpp
// 假设在某个编辑器上下文中
#include "ChaosClothGenerator.h"
#include "ClothGeneratorProperties.h"

// 1. 获取或创建生成器实例（通常由插件管理）
UE::Chaos::ClothGenerator::FChaosClothGenerator ChaosClothGenerator;

// 2. 配置属性（这些属性暴露在 UI 面板上）
UClothGeneratorProperties& Properties = ChaosClothGenerator.GetProperties();
Properties.SkeletalMeshAsset = MySkeletalMesh;
Properties.ClothAsset = MyChaosClothAsset;
Properties.AnimationSequence = MyAnimSequence;
Properties.FramesToSimulate = TEXT("0-10");
Properties.SimulatedCache = MyOutputCache;

// 3. 请求开始生成动作
// 这会设置 PendingAction 为 EClothGeneratorActions::StartGenerate
ChaosClothGenerator.RequestAction(UE::Chaos::ClothGenerator::EClothGeneratorActions::StartGenerate);

// 生成过程将在编辑器的 Tick 中异步执行（通过 Tick() 方法驱动）
// 用户可以在 UI 上看到进度，完成后 GeometryCache 被填充数据
```

### 进阶用法

该插件通过 `FChaosClothGeneratorToolsMenuExtender` 扩展了 ML Deformer 编辑器的工具栏和选项卡。以下代码展示了插件如何将自身集成到 ML Deformer 编辑器中。

```cpp
// 来自 Source/ChaosClothGenerator/Private/ChaosClothGeneratorToolsMenuExtender.h
// 实现 IToolsMenuExtender 接口，以注入菜单项和选项卡
namespace UE::Chaos::ClothGenerator
{
    // 创建一个工具菜单扩展器的工厂函数
    TUniquePtr<FChaosClothGeneratorToolsMenuExtender> CreateToolsMenuExtender();
}

// 在 ML Deformer 编辑器初始化时，会调用此类扩展器。
// FChaosClothGeneratorToolsMenuExtender 负责：
// 1. GetMenuEntry: 提供在“工具”菜单中的入口。
// 2. GetTabSummoner: 提供一个选项卡工厂，用于在编辑器中创建“Chaos Cloth Generator”面板。
//    该面板由 SClothGeneratorWidget 实现，其中包含了 UClothGeneratorProperties 的细节视图和触发生成的按钮。
```

## Demo 示例

该插件本身就是一个完整的编辑器工具，其源码即为最佳示例。以下代码片段展示了如何从 C++ 侧启动一个生成任务（概念演示）。

```cpp
// ChaosClothGeneratorDemo.h
#pragma once
#include "CoreMinimal.h"
#include "ChaosClothGenerator.h"

class FChaosClothGeneratorDemo
{
public:
    void RunDemo();

private:
    // 持有生成器实例
    TUniquePtr<UE::Chaos::ClothGenerator::FChaosClothGenerator> Generator;
};
```

```cpp
// ChaosClothGeneratorDemo.cpp
#include "ChaosClothGeneratorDemo.h"
#include "ClothGeneratorProperties.h"
#include "GeometryCache.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkinnedAsset.h"
#include "ClothAssetBase.h" // For UChaosClothAsset

void FChaosClothGeneratorDemo::RunDemo()
{
    // 1. 创建生成器
    Generator = MakeUnique<UE::Chaos::ClothGenerator::FChaosClothGenerator>();

    // 2. 获取并配置属性（需要有效的资产引用）
    if (Generator.IsValid())
    {
        UE::Chaos::ClothGenerator::FClothGeneratorProperties& Props = Generator->GetProperties();
        // 假设以下资产已存在并被正确加载
        // Props.SkeletalMeshAsset = LoadObject<USkinnedAsset>(...);
        // Props.ClothAsset = LoadObject<UChaosClothAsset>(...);
        // Props.AnimationSequence = LoadObject<UAnimSequence>(...);
        // Props.SimulatedCache = LoadObject<UGeometryCache>(...);
        Props.FramesToSimulate = TEXT("0, 5, 10"); // 只模拟三帧用于演示
        Props.NumSteps = 100; // 减少迭代次数以加快演示速度

        // 3. 启动生成
        Generator->RequestAction(UE::Chaos::ClothGenerator::EClothGeneratorActions::StartGenerate);
        UE_LOG(LogChaosClothGenerator, Log, TEXT("Generation request submitted. The task will run asynchronously in the editor tick."));
        // 注意：生成过程会在编辑器 Tick 中异步完成，此处无法直接等待结果。
        // 实际结果需要检查输出的 GeometryCache 资产。
    }
}
```

## 模块依赖

要使用此插件的功能（主要是其编辑器工具），你的项目需要启用以下插件依赖。在构建你自己的编辑器工具如果需要集成类似功能，可能需要引用这些模块。

| 模块 | 用途 |
|---|---|
| `MLDeformerFramework` | 机器学习变形器框架，是此插件的核心服务对象。 |
| `ChaosClothAsset` | 提供 `UChaosClothAsset` 类型，用于定义布料模拟的资产。 |
| `GeometryCache` | 提供 `UGeometryCache` 类型，用于存储生成的动画网格序列数据。 |
| `ChaosClothSimulation` | (隐式依赖) 底层的 Chaos 布料物理模拟引擎。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏更新为新的 UE_LOGF 格式，属于代码现代化。 |
| 2025-10-09 | `6f9a70e2` | Fix crash in Cloth Generator when there is no skeleton assigned to a cloth asset. | 修复当布料资产未指定骨架时生成器会崩溃的问题。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为源文件添加内联生成宏，优化编译，应用范围更广。 |
| 2025-04-10 | `130ca170` | Fix unity buld error | 修复 Unity 构建（合并编译）模式下的错误。 |
| 2025-01-30 | `1179af2c` | Chaos Cloth Asset - Made the cloth an inherited class of a new UChaosClothAssetBase class to prepare | 布料资产重构，引入 UChaosClothAssetBase 基类，为未来扩展做准备。 |

### 维护评价

- **创建时间**：2023年6月，约2年历史，相对年轻。
- **近期活跃度**：**活跃维护**。最后一次功能性更新（修复崩溃）发生在约6个月前（2025-10-09），且近期仍有代码现代化的更新。这表明 Epic 仍在维护此插件。
- **状态**：**实验性** (`IsExperimentalVersion: true`)，且默认未启用。这意味着该功能尚未稳定，API 可能在未来版本中发生变化。
- **已知限制**：
    1. 作为**数据生成工具**，其输出依赖于输入资产的质量和模拟参数的设置。
    2. 模拟过程可能非常耗时，特别是对于长动画和高迭代次数，依赖 `NumThreads` 进行并行优化。
    3. 是编辑器专用插件，**不能**在打包后的游戏中运行。
- **推荐使用**：如果你正在使用 **ML Deformer** 工作流并需要生成布料模拟数据，**推荐使用**此插件。它是官方提供的自动化解决方案，比手动模拟高效得多。但请务必注意其**实验性**状态，在项目升级时需关注可能的 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/ChaosClothGenerator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) (无特定文档，属于 ML Deformer 生态的一部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/ChaosClothGenerator) (插件源码本身包含自检逻辑，但无独立的测试目录)