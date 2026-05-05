# Deformer Graph

> Editor for creating GPU mesh deformation graphs

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、示例资源） |
| 模块 | `OptimusSettings` (Runtime), `OptimusCore` (Runtime), `OptimusDeveloper` (UncookedOnly), `OptimusEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph) | |

---

## 用途

Deformer Graph（内部代号 **Optimus**）是 UE5 的 **GPU 网格变形图编辑器**。它提供了一个基于节点的可视化编程环境，让开发者和技术美术能够在 GPU 上构建自定义的网格变形管线。

**核心解决的问题**：传统的 CPU 端骨骼网格变形（Skinning）在面对大量顶点或复杂变形逻辑时会成为性能瓶颈。Deformer Graph 将变形计算卸载到 GPU Compute Shader 上执行，允许用户通过节点图自由组合变形操作（蒙皮、Morph Target、自定义位移等），实现高性能的自定义变形管线。

**为什么存在**：
- UE5 内置的变形器（如骨骼蒙皮）是硬编码的，无法灵活扩展
- 传统方案要实现自定义 GPU 变形需要编写大量 C++ 和 Shader 代码
- Deformer Graph 将这个过程可视化、模块化，大幅降低 GPU 变形开发门槛
- 与 ControlRig 深度集成，可以直接在变形图中访问骨骼控制数据

**底层依赖**：
- **ComputeFramework**：提供 GPU Compute 调度抽象层
- **ControlRig**：提供骨骼控制数据的访问能力

---

## 使用场景

- 你在做一个角色密集的大型游戏，需要自定义 GPU 蒙皮变形以提升性能 → 用 Deformer Graph
- 你需要实现基于物理的布料/肌肉变形效果，且要求在 GPU 上运行 → 用 Deformer Graph
- 你想在不写 Shader 的情况下，通过可视化节点组合出复杂的变形逻辑 → 用 Deformer Graph
- 你需要将 ControlRig 的骨骼数据作为输入，驱动自定义的 GPU 变形 → 用 Deformer Graph
- 你正在做影视级实时渲染，需要精细控制每个顶点的变形行为 → 用 Deformer Graph

---

## 架构概览

Deformer Graph 采用四模块架构：

```
┌─────────────────────────────────────────────────────────┐
│                    OptimusEditor (Editor)                │
│         可视化节点图编辑器、剪贴板、搜索功能              │
├─────────────────────────────────────────────────────────┤
│                  OptimusDeveloper (UncookedOnly)         │
│              开发者工具、调试辅助、仅编辑器可用            │
├─────────────────────────────────────────────────────────┤
│                   OptimusCore (Runtime)                  │
│    核心运行时：Deformer 资产、节点图、数据绑定、GPU 调度    │
├─────────────────────────────────────────────────────────┤
│                  OptimusSettings (Runtime)               │
│              插件配置、项目设置                            │
└─────────────────────────────────────────────────────────┘
         ↕                    ↕
   ComputeFramework        ControlRig
```

### 核心概念

| 概念 | 说明 |
|---|---|
| **UOptimusDeformer** | 变形器资产，是整个图的根对象，附加到 SkeletalMeshComponent 上 |
| **UOptimusNodeGraph** | 节点图容器，包含多个子图（Update Graph、Setup Graph 等） |
| **UOptimusNode** | 单个节点，代表一个计算操作（数学运算、数据读写、自定义 Kernel 等） |
| **UOptimusComponentSource** | 组件数据源，定义变形图可以访问哪些组件数据 |
| **UOptimusResourceDescription** | 资源描述，定义 GPU Buffer 的数据格式和绑定 |
| **UOptimusDeformerInstance** | 运行时实例，管理变形器在具体组件上的执行状态 |

---

## 蓝图用法

> ⚠️ **注意**：Deformer Graph 主要是编辑器工具 + 运行时 GPU 调度系统，大部分交互通过编辑器 UI 完成。以下是从 OptimusCore 模块提取的运行时可用 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetDeformer` | 为 SkeletalMeshComponent 设置变形器资产 | `UOptimusDeformerInstance` |
| `GetDeformer` | 获取当前绑定的变形器资产 | `UOptimusDeformerInstance` |
| `TriggerReset` | 触发变形器重置（重新执行 Setup Graph） | `UOptimusDeformerInstance` |

### 使用示例（蓝图描述）

**在运行时为角色设置自定义变形器**：

1. 在角色蓝图中，获取 `Skeletal Mesh Component` 引用
2. 通过 `Get Deformer Instance` 节点获取或创建 `OptimusDeformerInstance`
3. 使用 `Set Deformer` 节点，将你创建好的 `UOptimusDeformer` 资产赋值给实例
4. 变形器会在下一帧自动开始 GPU 调度执行

**典型蓝图流程**：
```
[BeginPlay] → [Get Skeletal Mesh Component] → [Get Deformer Instance]
    → [Set Deformer (引用你的 .optimus 资产)] → [完成]
```

---

## C++ 用法

### 头文件引入

```cpp
// 核心运行时
#include "OptimusDeformer.h"
#include "OptimusNodeGraph.h"
#include "OptimusDeformerInstance.h"

// 编辑器模块（仅在 Editor 模块中使用）
#include "IOptimusEditorModule.h"
#include "OptimusEditorClipboard.h"
```

### 基本用法 — 编辑器模块接口

从 `IOptimusEditorModule.h` 提取的编辑器创建流程：

```cpp
// 来源: Engine/Plugins/Animation/DeformerGraph/Source/OptimusEditor/Public/IOptimusEditorModule.h

// 获取编辑器模块
IOptimusEditorModule& EditorModule = IOptimusEditorModule::Get();

// 创建变形器编辑器实例
UOptimusDeformer* DeformerAsset = /* 你的变形器资产 */;
TSharedRef<IOptimusEditor> Editor = EditorModule.CreateEditor(
    EToolkitMode::Standalone,  // 编辑器模式
    nullptr,                    // ToolkitHost（WorldCentric 模式时使用）
    DeformerAsset               // 要编辑的变形器对象
);
```

### 基本用法 — 剪贴板操作

从 `OptimusEditorClipboard.h` 提取的节点复制粘贴功能：

```cpp
// 来源: Engine/Plugins/Animation/DeformerGraph/Source/OptimusEditor/Public/OptimusEditorClipboard.h

// 将选中的节点复制到剪贴板
TArray<UOptimusNode*> SelectedNodes = /* 获取选中节点 */;
FOptimusEditorClipboard::SetClipboardFromNodes(SelectedNodes);

// 检查剪贴板是否有有效内容
if (FOptimusEditorClipboard::HasValidClipboardContent())
{
    // 从剪贴板内容创建节点图（用于粘贴操作）
    UOptimusNodeGraph* PastedGraph = FOptimusEditorClipboard::GetGraphFromClipboardContent(
        TargetPackage
    );
}
```

### 进阶用法 — 搜索功能

从 `FindInDeformer.h` 提取的图内搜索实现：

```cpp
// 来源: Engine/Plugins/Animation/DeformerGraph/Source/OptimusEditor/Public/FindInDeformer.h

// SFindInDeformer 继承自 SFindInGraph，提供变形器图内的节点搜索
// 自定义搜索匹配逻辑通过重写 MatchTokensInNode 实现
// 搜索结果通过 FFindInDeformerResult::JumpToNode 跳转到对应节点

// 使用方式：在编辑器 UI 中嵌入搜索框
TSharedRef<SFindInDeformer> SearchWidget = SNew(SFindInDeformer);
```

---

## Demo 示例

### 最小运行时集成示例

以下示例展示如何在 C++ 中以编程方式为 SkeletalMeshComponent 绑定 Deformer Graph：

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UOptimusDeformer;
class UOptimusDeformerInstance;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    virtual void BeginPlay() override;

    // 要使用的变形器资产（在蓝图/编辑器中设置）
    UPROPERTY(EditAnywhere, Category = "Deformer")
    UOptimusDeformer* DeformerAsset;

private:
    UPROPERTY()
    UOptimusDeformerInstance* DeformerInstance;
};
```

```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "OptimusDeformer.h"
#include "OptimusDeformerInstance.h"
#include "Components/SkeletalMeshComponent.h"

AMyCharacter::AMyCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
    DeformerAsset = nullptr;
    DeformerInstance = nullptr;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();

    USkeletalMeshComponent* SkelMeshComp = GetMesh();
    if (!SkelMeshComp || !DeformerAsset)
    {
        return;
    }

    // DeformerInstance 会在组件初始化时自动创建
    // 通过设置 Deformer 资产来激活 GPU 变形管线
    // 具体 API 请参考 OptimusDeformerInstance 的公开接口
}
```

---

## 模块依赖

### 插件级依赖

| 插件 | 用途 |
|---|---|
| `ComputeFramework` | GPU Compute 调度抽象层，Deformer Graph 的所有 GPU 计算都通过此框架执行 |
| `ControlRig` | 提供骨骼控制数据访问，变形图中的骨骼输入节点依赖此插件 |

### 模块级依赖（独特依赖）

| 模块 | 用途 |
|---|---|
| `ComputeFramework` | GPU 计算调度 |
| `ControlRig` | 骨骼控制数据 |
| `OptimusCore` | 核心运行时（OptimusEditor 和 OptimusDeveloper 依赖） |
| `OptimusSettings` | 配置管理（OptimusCore 依赖） |
| `RenderCore` | 渲染核心，GPU 资源管理 |
| `RHI` | 渲染硬件接口，Compute Shader 调度 |
| `ShaderCore` | Shader 编译和管理 |

---

## 维护状态

### 近期更新

```
- 36bf499a13b6 Slate Dynamic Invalidation - ExpanderArrow（Slate UI 性能优化）
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files（代码生成宏更新）
- 4e05189769b6 Added ObjectInstancingGraph.h and added includes where needed（头文件依赖重构）
```

### 维护评价

**综合评价：活跃维护中，但仍是实验性功能**

- **创建时间**：2022 年 8 月，随 UE5 早期版本发布，约 3 年历史
- **实验性标记**：`IsBetaVersion=true`，`EnabledByDefault=false`——需要手动启用，API 可能在未来版本中发生变化
- **更新频率**：近期 commit 主要是编译修复和代码质量改进（如内联宏、头文件整理），而非功能性更新
- **代码规模**：536 个源文件，属于大型插件，说明功能已经相当完善
- **依赖关系**：依赖 ComputeFramework 和 ControlRig 两个同样活跃维护的插件
- **已知限制**：
  - Beta 状态意味着 API 不稳定，升级引擎版本时可能需要适配
  - 需要支持 Compute Shader 的 GPU（SM5+）
  - 调试 GPU 变形图比 CPU 代码更困难

**推荐使用**：✅ 推荐。如果你的项目需要自定义 GPU 变形管线，这是 UE5 官方提供的最佳方案。虽然标记为 Beta，但 Epic 自己的项目（如 Fortnite）已经在使用。建议锁定引擎版本使用，升级时做好适配准备。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph)
- 官方文档（暂无）
- [ComputeFramework 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/DeformerGraph)（依赖插件）
- [ControlRig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)（依赖插件）