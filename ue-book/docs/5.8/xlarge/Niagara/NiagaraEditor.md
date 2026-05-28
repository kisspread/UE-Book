# Niagara

> Niagara effect systems.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉特效系统 |
| 分类 | FX |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、示例系统、编辑器工具、参数定义库） |
| 模块 | `NiagaraCore` (Runtime), `Niagara` (Runtime), `NiagaraShader` (Runtime), `NiagaraVertexFactories` (Runtime), `NiagaraAnimNotifies` (Runtime), `NiagaraBlueprintNodes` (Runtime), `NiagaraEditor` (Runtime), `NiagaraEditorWidgets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2017-08-28 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara) | |

## 用途

Niagara 是 Unreal Engine 的下一代可编程特效系统，旨在解决旧版 Cascade 粒子系统在性能、灵活性和可扩展性方面的局限性。它提供了一个基于节点的、高度可视化且数据驱动的编辑器，允许开发者创建从简单的粒子效果到复杂的、可与游戏逻辑深度交互的 GPU 计算特效。其核心设计哲学是“一切皆可编程”，通过一个统一的、支持蓝图和 HLSL 的脚本系统，让用户可以精确控制粒子的每一个生命阶段、数据接口（Data Interface）以及渲染行为。

## 使用场景

-   **大规模粒子特效**：你需要在 GPU 上处理数以万计的粒子，用于火焰、烟雾、魔法效果等。
-   **复杂游戏性特效**：你需要粒子系统能够读取并响应游戏世界中的数据（如角色位置、速度），例如追踪导弹、根据地面材质改变脚步尘土效果。
-   **程序化动画与渲染**：你需要完全控制粒子的生成、运动、更新和渲染流程，实现非标准的视觉效果。
-   **蓝图快速原型**：你希望使用蓝图节点快速搭建特效逻辑，而无需编写 HLSL 代码。
-   **团队协作与版本控制**：你需要一个清晰的、模块化的特效编辑界面，便于美术和程序员协作，并支持版本继承。

## 蓝图用法

Niagara 编辑器模块提供了丰富的蓝图接口，主要用于控制特效的编译、调试和运行时交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CompileScript` | 启动指定脚本的编译。 | `FNiagaraEditorModule` |
| `GetCompilationResult` | 获取编译任务的结果（阻塞或非阻塞）。 | `FNiagaraEditorModule` |
| `RequestCompileSystem` | 请求编译整个 Niagara 系统。 | `FNiagaraEditorModule` |
| `PollSystemCompile` | 轮询系统编译任务的状态。 | `FNiagaraEditorModule` |
| `MergeEmitter` | 合并发射器实例与父发射器的更改（继承）。 | `FNiagaraScriptMergeManager` |
| `DiffEmitters` | 比较两个发射器的差异。 | `FNiagaraScriptMergeManager` |
| `ResetModuleInputToBase` | 将模块输入重置为父级（基础）值。 | `FNiagaraScriptMergeManager` |

### 使用示例（蓝图描述）

1.  **触发系统编译**：在蓝图中，通过 `RequestCompileSystem` 节点传入 `UNiagaraSystem` 对象和 `bForce` 参数，异步启动系统编译。
2.  **监控编译状态**：使用 `PollSystemCompile` 节点，在每一帧或定时检查编译句柄，以获取编译进度或结果。
3.  **处理发射器继承**：在自定义的发射器编辑工具中，使用 `DiffEmitters` 对比子发射器与父发射器的差异，然后使用 `MergeEmitter` 将父级的更新应用到子发射器。

## C++ 用法

主要的编程接口集中在 `NiagaraEditor` 模块中，通过 `FNiagaraEditorModule` 单例访问。

### 头文件引入

```cpp
#include "NiagaraEditorModule.h"
#include "NiagaraScriptMergeManager.h"
```

### 基本用法

以下示例展示了如何通过 C++ 接口编译一个脚本并获取结果。

```cpp
// 获取 Niagara 编辑器模块实例
FNiagaraEditorModule& NiagaraEditorModule = FModuleManager::Get().LoadModuleChecked<FNiagaraEditorModule>(TEXT("NiagaraEditor"));

// 假设我们有一个要编译的 UNiagaraScript 资产
UNiagaraScript* ScriptToCompile = ...;

// 准备编译选项
FNiagaraCompileOptions CompileOptions;
// ... 设置其他选项

// 启动编译
int32 JobID = NiagaraEditorModule.CompileScript(CompileRequestData, CompileRequestDuplicateData, CompileOptions);

// 在后续的 Tick 或适当的时间点获取结果
bool bWait = true; // 是否阻塞等待
FNiagaraScriptCompileMetrics Metrics;
TSharedPtr<FNiagaraVMExecutableData> Result = NiagaraEditorModule.GetCompilationResult(JobID, bWait, Metrics);

if (Result.IsValid())
{
    // 编译成功，处理结果
}
```
*来源: `Public/NiagaraEditorModule.h` 中 `FNiagaraEditorModule` 类的定义*

### 进阶用法

使用 `FNiagaraScriptMergeManager` 来管理发射器的继承和差异比较。

```cpp
// 获取脚本合并管理器实例
TSharedRef<FNiagaraScriptMergeManager> MergeManager = NiagaraEditorModule.GetScriptMergeManager();

// 假设有两个版本的发射器：ParentEmitter 和 InstanceEmitter
FVersionedNiagaraEmitter ParentEmitter = ...;
FVersionedNiagaraEmitter InstanceEmitter = ...;

// 1. 比较差异
FNiagaraEmitterDiffResults DiffResults = MergeManager->DiffEmitters(ParentEmitter, InstanceEmitter);

// 2. 检查特定模块是否被修改
if (DiffResults.IsValid() && !DiffResults.IsEmpty())
{
    // 例如，检查粒子生成脚本栈的差异
    const FNiagaraScriptStackDiffResults& ParticleSpawnDiff = DiffResults.ParticleSpawnDiffResults;
    
    // 处理被移除、添加或修改的模块
    // ...
    
    // 3. 将父级的某个模块输入重置到基础值
    ENiagaraScriptUsage Usage = ENiagaraScriptUsage::ParticleSpawnScript;
    FGuid ScriptUsageId = FGuid(); // 具体的用法ID
    FGuid ModuleId = ...; // 模块的ID
    FString InputName = TEXT("MyInput");
    
    MergeManager->ResetModuleInputToBase(InstanceEmitter, ParentEmitter, Usage, ScriptUsageId, ModuleId, InputName);
}
```
*来源: `Private/NiagaraScriptMergeManager.h` 中 `FNiagaraScriptMergeManager` 类的定义*

## Demo 示例

一个最小的、展示如何通过 C++ 触发 Niagara 系统编译的示例。

### 头文件 `MyNiagaraHelper.h`
```cpp
#pragma once
#include "CoreMinimal.h"

class UNiagaraSystem;

class FMyNiagaraHelper
{
public:
    static void RequestSystemCompilation(UNiagaraSystem* System);
};
```

### 实现文件 `MyNiagaraHelper.cpp`
```cpp
#include "MyNiagaraHelper.h"
#include "NiagaraEditorModule.h"
#include "NiagaraSystem.h"

void FMyNiagaraHelper::RequestSystemCompilation(UNiagaraSystem* System)
{
    if (!System) return;

    FNiagaraEditorModule& NiagaraModule = FModuleManager::Get().LoadModuleChecked<FNiagaraEditorModule>(TEXT("NiagaraEditor"));
    
    // 强制重新编译
    const bool bForce = true;
    const ITargetPlatform* TargetPlatform = nullptr; // 或指定特定平台
    
    FNiagaraCompilationTaskHandle TaskHandle = NiagaraModule.RequestCompileSystem(System, bForce, TargetPlatform);
    
    if (TaskHandle.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Niagara system '%s' compilation requested. Handle: %s"), *System->GetName(), *TaskHandle.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to request compilation for Niagara system '%s'"), *System->GetName());
    }
}
```

## 模块依赖

要使用 Niagara 的编辑器功能（如编译、合并），你的模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `NiagaraCore` | Niagara 的核心运行时类型、定义和基础数据结构。 |
| `Niagara` | Niagara 的主要运行时逻辑，包括系统、发射器、脚本的执行。 |
| `NiagaraShader` | 与 Niagara GPU 着色器编译和管理相关的代码。 |
| `NiagaraVertexFactories` | Niagara 使用的自定义顶点工厂，用于渲染粒子。 |
| `NiagaraEditor` | **（关键）** 所有编辑器功能的核心，包括编译器、合并管理器、工具包等。 |
| `NiagaraEditorWidgets` | Niagara 编辑器中使用的自定义 UI 控件和组件。 |

*注：你的 `Build.cs` 文件中应包含 `PublicDependencyModuleNames.AddRange(new string[] { "NiagaraCore", "NiagaraEditor" });` 等。具体依赖请根据实际使用的 API 确定。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `da97a493` | Data Hierarchy: guard SyncViewModelsToData against re-entry from OnHierarchyChanged listeners | 修复数据层级视图中 `SyncViewModelsToData` 可能被 `OnHierarchyChanged` 回调重入的问题，增强了稳定性。 |
| 2026-05-22 | `85c6d110` | - Avoid creating an empty RHI buffer for SKM sampling data | 优化骨骼网格体（SKM）采样数据，避免创建不必要的空 RHI 缓冲区，可能提升性能。 |
| 2026-05-20 | `119ee9ac` | [HWRT] Fix FNiagaraRendererMeshes::GetDynamicRayTracingInstances(...) corrupting GPUScene when rende | 修复硬件光线追踪（HWRT）模式下，网格渲染器在获取动态光线追踪实例时可能损坏 GPUScene 的问题。 |
| 2026-05-19 | `5e68c5a9` | [HWRT] Fix crash due to FNiagaraRendererRibbons requesting multiple updates on the same RayTracingGe | 修复带状渲染器（Ribbons）在硬件光线追踪下，因对同一几何体请求多次更新而导致的崩溃。 |
| 2026-05-14 | `4bb8e4f1` | Fix UNiagaraBakerSettings crash when AI toolset or Python writes a null entry into the Outputs array | 修复当 AI 工具或 Python 脚本向 `UNiagaraBakerSettings` 的 `Outputs` 数组写入空条目时可能导致的崩溃。 |

### 维护评价

**积极维护，核心活跃组件**。
-   **创建时间**：2017 年 8 月，是 UE 的资深插件。
-   **近期更新**：**极度活跃**。截至 2026 年 5 月仍有频繁的功能性更新和 Bug 修复，特别是围绕 **硬件光线追踪 (HWRT)**、**编译系统**、**编辑器稳定性** 等核心功能。
-   **维护状态**：作为 UE 的官方下一代特效系统，Niagara 处于 **持续积极的维护和迭代** 中。
-   **已知问题/限制**：作为极其复杂和庞大的系统，可能存在一些边缘情况下的性能或兼容性问题，但 Epic 团队在持续修复。
-   **推荐使用**：**强烈推荐**。它是 UE5 中创建高性能、可编程特效的 **标准且推荐** 的解决方案，适用于所有规模的项目。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/creating-visual-effects-in-niagara-for-unreal-engine/) (通用链接，非 .uplugin 中指定，但为官方文档入口)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/Niagara/Tests) (路径推断，实际位置可能有变化)