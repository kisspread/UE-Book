# Niagara

> Niagara effect systems.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉粒子系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、示例） |
| 模块 | `Niagara` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraCore` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

## 用途

Niagara 是虚幻引擎 5 的下一代视觉效果系统，用于创建复杂的粒子效果、环境效果和动态视觉特效。它替代了旧的级联 (Cascade) 粒子系统，提供了更强大、更灵活的架构，主要优势包括：

*   **面向数据的架构**: 粒子数据以高度优化的方式存储和处理，支持大规模粒子模拟。
*   **GPU 计算支持**: 可以将大部分模拟计算（如物理、力场）卸载到 GPU 上执行，大幅提升性能。
*   **模块化与可复用性**: 效果由一系列可重用的模块组成，可以在不同发射器和系统间共享逻辑。
*   **强大的事件与数据驱动**: 支持粒子间、发射器间以及与游戏世界的复杂事件和数据交互。
*   **蓝图与 C++ 深度集成**: 提供完整的蓝图节点库和 C++ API，便于程序化生成和控制效果。
*   **数据通道 (Data Channel)**: 一种高效的通信机制，允许粒子系统与游戏逻辑、动画、材质等进行双向、结构化数据交换。

它旨在解决 Cascade 在性能、灵活性和可扩展性方面的限制，是创建 AAA 级游戏和高保真视觉效果的首选工具。

## 使用场景

*   你需要创建一个高性能的爆炸、魔法、火焰或天气系统，包含数百万粒子，并需要复杂的物理交互 → 用 Niagara 的 GPU 计算模块。
*   你的游戏技能系统需要根据玩家输入或游戏状态（如血量、元素反应）动态改变特效表现 → 用 Niagara 的蓝图事件和数据通道。
*   你需要让粒子效果与骨骼动画（如角色施法时粒子从骨骼发出）、地形（如雪地脚印）或物理对象（如子弹轨迹）精确绑定 → 用 Niagara 的网格采样、Skeletal Mesh 模块。
*   你需要一个在编辑器中实时预览，并能轻松与程序逻辑交互的现代化粒子编辑器 → 用 Niagara Editor。

## 蓝图用法

**重要**: 由于 Niagara 是一个庞大的系统，蓝图节点数量极多。以下仅列出 `NiagaraBlueprintNodes` 模块中提供的**核心数据通道 (Data Channel) 相关节点**，这些是 Niagara 与游戏逻辑交互的关键高级功能。更多基础节点（如发射器控制）请查阅引擎内蓝图库。

### 核心节点

#### 数据通道操作节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `WriteToNiagaraDataChannel` | 向 Niagara 数据通道写入数据。 | `UK2Node_WriteDataChannel` |
| `ReadFromNiagaraDataChannel` | 从 Niagara 数据通道读取数据。 | `UK2Node_ReadDataChannel` |
| `WriteToNiagaraDataChannelSingle` | 向数据通道写入单个元素的数据（展开为多个变量设置调用）。 | `UK2Node_WriteDataChannelSingle` |
| `ReadFromNiagaraDataChannelSingle` | 从数据通道读取单个元素的数据（展开为多个变量获取调用）。 | `UK2Node_ReadDataChannelSingle` |
| `GetDataChannelElementCount` | 获取数据通道中当前有效的元素数量。 | `UK2Node_DataChannelGetNum` |

#### 数据通道访问上下文节点 (高级)
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Make Access Context` | 创建一个用于访问数据通道的上下文结构体。 | `UK2Node_DataChannelAccessContext_Make` |
| `Get Members from Access Context` | 从访问上下文中获取成员变量。 | `UK2Node_DataChannelAccessContext_GetMembers` |
| `Set Members in Access Context` | 设置访问上下文中的成员变量。 | `UK2Node_DataChannelAccessContext_SetMembers` |
| `Prepare Access Context` | 准备一个可用的访问上下文，用于后续的数据通道访问。 | `UK2Node_DataChannelAccessContext_Prepare` |

### 使用示例（蓝图描述）

**场景：从游戏逻辑向 Niagara 系统发送颜色和位置信息**

1.  **在蓝图中创建变量**：创建两个变量，例如 `MyColor` (Linear Color) 和 `MyLocation` (Vector)。
2.  **创建数据通道资产**：在内容浏览器中右键创建 `Niagara Data Channel Asset`，并定义其中包含 `Color` 和 `Location` 两个变量。
3.  **写入数据**：
    *   拖拽 `WriteToNiagaraDataChannel` 节点到图表中。
    *   在 `Data Channel` 引脚上指定你创建的数据通道资产。
    *   连接 `Execution` 引脚。
    *   将 `MyColor` 和 `MyLocation` 变量连接到该节点自动生成的对应输入引脚。
4.  **在 Niagara 系统中接收**：
    *   在 Niagara 编辑器的发射器更新脚本中，添加 `Data Channel Receiver` 模块。
    *   在模块设置中指定相同的数据通道资产。
    *   将接收到的 `Color` 和 `Location` 数据用于驱动粒子的颜色或位置属性。

**注意**：蓝图中的节点在编译时会根据所选数据通道资产的定义自动展开生成对应的变量引脚。对于更复杂的结构体数据，需要使用访问上下文节点进行操作。

## C++ 用法

`NiagaraBlueprintNodes` 模块主要为蓝图提供节点，其 C++ 用法较少被直接用于效果创建。更核心的 Niagara C++ API 位于 `Niagara` 和 `NiagaraCore` 模块中。以下是一个基础示例，展示如何从 C++ 中通过数据通道向 Niagara 系统发送数据。

### 头文件引入

```cpp
#include "NiagaraDataChannel.h"
#include "NiagaraDataChannelAccessor.h"
#include "NiagaraFunctionLibrary.h"
```

### 基本用法

```cpp
// 假设你已经有一个指向 UNiagaraDataChannel 的指针和一个 NiagaraComponent
void SendDataToNiagaraSystem(UNiagaraDataChannel* DataChannel, UNiagaraComponent* NiagaraComp)
{
    if (!DataChannel || !NiagaraComp)
    {
        return;
    }

    // 1. 创建一个数据通道访问器
    FNiagaraDataChannelAccessor Accessor;
    Accessor.Init(DataChannel, ENiagaraResourceAccess::Write);

    // 2. 准备写入（获取一个可写的“槽位”）
    FNiagaraDataChannelSearchParameters SearchParams;
    if (Accessor.PrepareForWrite(SearchParams))
    {
        // 3. 向当前槽位写入数据
        // 假设数据通道中有一个名为 “Health” 的 Float 变量和一个名为 “Color” 的 LinearColor 变量
        Accessor.SetFloatValue(FName("Health"), 100.0f);
        Accessor.SetColorValue(FName("Color"), FLinearColor::Green);

        // 4. 完成本次写入，将数据提交到通道
        Accessor.CommitWrite();
    }
}
```
*（注：以上代码为基于 `FNiagaraDataChannelAccessor` 常见用法的概念性示例，具体 API 调用请参考最新引擎源码和文档。）*

### 进阶用法

结合多个模块实现程序化生成效果：

```cpp
// 程序化创建一个 Niagara System Component 并在世界中生成
void SpawnProgrammaticNiagaraEffect(UWorld* World, UNiagaraSystem* NiagaraSystem, FVector Location)
{
    UNiagaraComponent* NiagaraComp = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
        World,
        NiagaraSystem,
        Location,
        FRotator::ZeroRotator,
        FVector(1.0f),
        true,
        true,
        ENCPoolMethod::None,
        true
    );

    if (NiagaraComp)
    {
        // 可以通过 C++ 接口设置系统用户参数
        NiagaraComp->SetVariableFloat(FName("User.Lifetime"), 5.0f);
        NiagaraComp->SetVariableLinearColor(FName("User.Color"), FLinearColor::Red);
        // 还可以通过数据通道与之交互，如上例所示。
    }
}
```

## Demo 示例

由于 Niagara 过于复杂，无法提供单一的最小可编译示例。官方引擎和 Marketplace 提供了大量示例项目和资产。一个典型的入门方式是：

1.  在编辑器中创建一个新的 `Niagara System` 资产。
2.  选择一个简单的模板，如 `Fountain` 或 `Sparkle`。
3.  在 `Niagara Editor` 中查看其模块组成。
4.  尝试修改发射器属性（如发射率、生命周期）和模块参数（如力、大小缩放）。
5.  创建一个 `Niagara Data Channel`，并尝试在蓝图或 C++ 中向其写入数据，在 Niagara 系统中读取并应用。

请参考官方文档和示例项目以获取详细教程。

## 模块依赖

从 `NiagaraBlueprintNodes.Build.cs` 提取。要用此模块提供的数据通道蓝图功能，你的模块通常需要依赖：

| 模块 | 用途 |
|---|---|
| `Niagara` | Niagara 核心运行时，包含系统、发射器、数据通道等基础类。 |
| `NiagaraCore` | Niagara 的核心类型和基础数据结构定义。 |
| `NiagaraEditor` | 提供蓝图节点编译支持，对蓝图节点模块通常是必要的。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 修复数据层级同步中的重入导致的潜在问题。 |
| 2026-05-22 | `85c6d110` | - Avoid creating an empty RHI buffer for SKM sampling data | 优化，避免为空的 SKM 采样数据创建 RHI 缓冲区。 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene when rende | 修复硬件光线追踪中动态实例获取导致的 GPU 场景损坏问题。 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGe | 修复丝带渲染器在硬件光线追踪中重复更新导致的崩溃。 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复烘焙设置在 AI 工具或 Python 脚本写入空值时的崩溃。 |

### 维护评价

**活跃维护**。Niagara 是虚幻引擎的核心组件之一，自 2017 年创建以来持续得到 Epic Games 的积极开发和维护。

*   **创建时间**: 2017 年，历史悠久。
*   **更新频率**: 非常高，近期的提交（2026 年 5 月）显示仍在进行新功能开发（数据层级、硬件光线追踪优化）、性能优化和 Bug 修复。
*   **维护状态**: **核心活跃**。作为 UE5 的默认粒子系统，其地位无可替代，必然会持续维护和迭代。
*   **已知问题/限制**: 作为复杂系统，学习曲线较陡峭，对 GPU 计算和模块化设计需要一定理解。硬件光线追踪等新特性可能仍在完善中。
*   **推荐使用**: **强烈推荐**。对于任何需要高质量、高性能视觉效果的 UE5 项目，Niagara 都是唯一且正确的选择。旧项目也应考虑从 Cascade 迁移至 Niagara。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/creating-visual-effects-in-niagara-for-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara/Tests)