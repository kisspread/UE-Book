# Chaos Flesh

> Chaos Flesh Simulation

| 属性 | 值 |
|---|---|
| 中文名 | 肉质模拟 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `ChaosFlesh` (Runtime), `ChaosFleshDeprecatedNodes` (Runtime), `ChaosFleshEditor` (Runtime), `ChaosFleshEngine` (Runtime), `ChaosFleshNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh) | |

## 用途

ChaosFlesh 是一个实验性插件，为 UE5 的 Chaos 物理系统提供了模拟**肉质物体**（Flesh）的能力。它旨在模拟和处理具有复杂体积、可变形及断裂特性的软体材料，例如生物组织、果冻、多孔材料等。其核心是 `FFleshCollection` 数据资产，它存储了用于物理模拟的拓扑、材质和骨骼信息，并利用 Dataflow 图进行程序化生成和处理，最终驱动 Chaos 物理求解器。

## 使用场景

- **角色破坏效果**：模拟角色受到重击后的软组织断裂、凹陷等。
- **生物/解剖模拟**：用于医学可视化、生物力学研究中的软组织交互。
- **破坏系统**：模拟木头、泡沫、多孔材料等脆性物体的碎裂过程。
- **程序化内容生成**：通过 Dataflow 图创建和驱动复杂的肉质几何体与物理行为。

## 蓝图用法

由于这是底层物理和资产生成系统，大部分核心逻辑在 C++ 和 Dataflow 图中。蓝图层面主要通过资产操作和引擎集成进行间接交互。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UFleshAsset` | 核心数据资产，封装 `FFleshCollection`，可在编辑器中创建和查看。 |
| `UFleshComponent` | 用于在场景 Actor 中加载和驱动 `UfleshAsset` 进行模拟的组件。 |

### 使用示例（蓝图描述）

1.  **创建资产**：在内容浏览器中右键，创建 `FleshAsset`。通过打开此资产，可使用 Dataflow 编辑器编辑其生成逻辑。
2.  **Actor 模拟**：在场景中放置一个 Actor，为其添加 `FleshComponent`。在组件细节面板中指定之前创建的 `FleshAsset`。游戏运行时，该组件将加载资产并驱动 Chaos 物理模拟。

## C++ 用法

### 头文件引入

```cpp
#include “FleshAsset.h”
#include “FleshComponent.h”
```

### 基本用法

（示例来自 `ChaosFleshEngine` 模块，展示如何以编程方式创建组件）

```cpp
// 假设在一个 Actor 的构造函数或BeginPlay中
UFleshComponent* FleshComp = CreateDefaultSubobject<UFleshComponent>(TEXT(“MyFlesh”));

// 加载一个已创建的 Flesh 资产
TSoftObjectPtr<UFleshAsset> AssetPath(TEXT(“/Game/MyFleshAssets/MyFlesh”));
FleshComp->SetFleshAsset(AssetPath.LoadSynchronous());
```

### 进阶用法

高级用法涉及直接操作 `FFleshCollection` 和 Dataflow 图进行程序化生成。这通常在编辑器工具或自定义 Dataflow 节点中完成，而非直接在运行时。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | 底层物理引擎框架。 |
| `GeometryCollectionEngine` | 与 Chaos 破坏系统共享基础设施（如集合管理器）。 |
| `Dataflow` | 提供用于程序化生成资产的图形化节点编辑系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-12 | `981bc9da` | Dataflow: | 提交信息不完整，疑似与 Dataflow 功能相关的更新。 |
| 2026-05-12 | `4bb4d4eb` | Flesh : fiber field generation node clean up | 清理了用于生成纤维场的 Dataflow 节点。 |
| 2026-05-12 | `3ee54b1a` | PR #13147: Fix NumMaskBuffer assignment from OffsetsBuffer to MaskBuffer | 修复了从偏移缓冲区到掩码缓冲区赋值的错误。 |
| 2026-05-12 | `563a0190` | Flesh : deprecate StaticMesh property from the flesh asset | 从肉质资产中废弃了静态网格体属性，表明其结构向纯物理数据演进。 |

### 维护评价

- **状态**: **实验性且活跃维护中**。
- **分析**:
    1.  **实验性**: `.uplugin` 明确标记为实验版本，默认未启用。
    2.  **活跃**: 最近一周内（2026年5月）有多次提交，内容涉及功能清理、Bug修复和架构优化（废弃旧属性），表明开发仍在积极推进。
    3.  **年龄**: 诞生于 2022 年，约 4 年历史，对于一个实验性模块来说处于成熟期。
    4.  **建议**: 该插件功能前沿且复杂，适合用于原型开发和技术研究。在生产环境中使用前，需充分测试其稳定性和性能，并准备好应对其 API 和功能可能发生的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ChaosFlesh)