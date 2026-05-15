# Niagara Toolsets

> A collection of tool calls allowing an AI assistant the ability to interact with Niagara.

| 属性 | 值 |
|---|---|
| 中文名 | 尼亚加拉工具集 |
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `NiagaraToolsets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/NiagaraToolsets) | |

## 用途

NiagaraToolsets 是一套面向 **AI 助手**的 Niagara 编辑器工具集，让 AI 能够以编程方式完整地创建、检查和修改 Niagara 特效系统。

它解决的核心问题是：AI 助手无法直接操作 Niagara 编辑器的复杂 UI，但可以通过这套结构化的 API 完成等效工作。具体覆盖以下能力层次：

1. **资产发现**：在项目中搜索和浏览 Niagara 脚本资产（模块、动态输入等），无需加载对象
2. **Schema 发现**：查询系统/发射器/模块/渲染器等各层级的属性结构和类型定义
3. **拓扑检查**：遍历 Niagara 系统的完整结构（发射器堆栈、模块、输入），但不读取具体数值
4. **数据读写**：读取和写入各个层级的具体属性值
5. **结构编辑**：添加/删除发射器、模块、渲染器，修改堆栈结构
6. **诊断**：获取编译状态和堆栈问题，应用自动修复
7. **Blueprint 封装**：将 Niagara 系统包装为可复用的 Blueprint Actor

所有函数都标记为 `AICallable`，通过 ToolsetRegistry 注册给 AI 助手调用。

## 使用场景

- 你想让 AI 助手从零创建一个 Niagara 粒子特效系统 → 用 `CreateNiagaraSystem` + `AddEmitter` + `AddModule`
- 你需要 AI 助手理解现有 Niagara 系统的结构 → 用 `GetSystemSummary` → `GetEmitterTopology` 分层遍历
- 你想让 AI 修改 Niagara 系统的属性值 → 用 `GetSystemData` / `SetSystemData` 读写
- 你需要 AI 在项目中查找可用的 Niagara 模块 → 用 `FindNiagaraScripts` 搜索资产注册表
- 你想让 AI 处理 Niagara 的编译错误 → 用 `GetStackIssues` + `ApplyStackIssueFix` 诊断修复
- 你想快速将 Niagara 系统包装成 Blueprint Actor → 用 `ConstructNiagaraBPWrapperFromSystem`

> **注意**：此插件默认禁用（`EnabledByDefault: false`），需在插件管理器中手动启用。它是实验性插件，仅在编辑器中可用。

## 蓝图用法

所有函数均为 `static` 且通过 `UFUNCTION(meta = (AICallable))` 暴露，可从蓝图直接调用。按功能分为以下几组：

### 系统操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateNiagaraSystem` | 基于模板创建新 Niagara 系统资产 | `UNiagaraToolset_System` |
| `GetSystemSummary` | 获取系统轻量级摘要（名称、用户变量、发射器列表） | `UNiagaraToolset_System` |
| `GetSystemSchema` | 获取系统级属性的 Schema（可设置的属性和类型） | `UNiagaraToolset_System` |
| `GetSystemData` / `SetSystemData` | 读取/写入系统级属性值 | `UNiagaraToolset_System` |
| `GetUserVariables` | 获取系统上定义的所有用户变量 | `UNiagaraToolset_System` |
| `AddUserVariables` / `RemoveUserVariables` | 添加/删除系统用户变量 | `UNiagaraToolset_System` |
| `GetSystemDependencies` | 获取系统的完整依赖汇总（渲染器、数据接口、模块、动态输入） | `UNiagaraToolset_System` |

### 发射器操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddEmitter` / `RemoveEmitter` | 向系统添加/移除发射器 | `UNiagaraToolset_System` |
| `GetEmitterSummary` | 获取发射器轻量级元数据 | `UNiagaraToolset_System` |
| `GetEmitterTopology` | 获取发射器完整拓扑（四个脚本堆栈 + 渲染器） | `UNiagaraToolset_System` |
| `GetEmitterData` / `SetEmitterData` | 读取/写入发射器属性值 | `UNiagaraToolset_System` |
| `GetEmitterInputValues` | 获取发射器所有模块的已解析输入值 | `UNiagaraToolset_System` |

### 模块与堆栈操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddModule` / `RemoveModule` | 向脚本堆栈添加/移除模块 | `UNiagaraToolset_System` |
| `SetModuleEnabled` | 启用/禁用堆栈中的模块 | `UNiagaraToolset_System` |
| `GetModuleSchema` / `GetModuleSchemaFromAsset` | 获取模块的输入 Schema | `UNiagaraToolset_System` |
| `GetModuleTopology` | 获取模块拓扑（元数据 + 所有输入，无值） | `UNiagaraToolset_System` |
| `GetModuleInputValues` | 获取单个模块的所有已解析输入值 | `UNiagaraToolset_System` |
| `AddSetParametersModule` | 添加 SetParameters 模块（直接设置参数） | `UNiagaraToolset_System` |
| `AddSetParameterEntry` / `RemoveSetParameterEntry` | 向 SetParameters 模块添加/移除参数 | `UNiagaraToolset_System` |
| `SetStackInputData` | 设置堆栈模块输入的值 | `UNiagaraToolset_System` |
| `GetDynamicInputChain` | 递归遍历动态输入链（拓扑 + 解析值） | `UNiagaraToolset_System` |

### 渲染器操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddRenderer` / `RemoveRenderer` | 向发射器添加/移除渲染器 | `UNiagaraToolset_System` |
| `GetRendererSchema` | 获取渲染器类的属性 Schema | `UNiagaraToolset_System` |
| `GetRendererData` / `SetRendererData` | 读取/写入渲染器属性值 | `UNiagaraToolset_System` |

### 诊断节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSystemCompileState` | 获取系统编译状态（异步） | `UNiagaraToolset_System` |
| `GetStackIssues` | 获取所有堆栈问题（错误、警告、信息）（异步） | `UNiagaraToolset_System` |
| `ApplyStackIssueFix` | 应用堆栈问题的自动修复（异步，可撤销） | `UNiagaraToolset_System` |

### 资产发现节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAssetDiscoveryInfo` | 获取项目配置的资产发现分组 | `UNiagaraToolset_Assets` |
| `FindNiagaraScripts` | 按条件搜索 Niagara 脚本资产（仅读取资产注册表，不加载对象） | `UNiagaraToolset_Assets` |
| `GetNiagaraScriptDigest` | 获取脚本资产的解码元数据 | `UNiagaraToolset_Assets` |

### 组件操作节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSystem` | 设置组件的 Niagara 系统 | `UNiagaraToolset_Component` |
| `GetUserVariables` (Component) | 获取组件上的用户变量值 | `UNiagaraToolset_Component` |
| `SetVariable` / `GetVariable` | 设置/获取组件的用户变量覆盖值 | `UNiagaraToolset_Component` |

### Blueprint 封装节点

| 节点 | 说明 | 所所在类 |
|---|---|---|
| `ConstructNiagaraBPWrapperFromSystem` | 从 Niagara 系统创建 Blueprint Actor 包装器 | `UNiagaraToolset_Blueprint` |
| `ConstructNiagaraBPWrapperFromComponent` | 从 Niagara 组件创建 Blueprint Actor 包装器（保留属性覆盖） | `UNiagaraToolset_Blueprint` |

### 信息查询节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UEnum_Info` | 获取 UEnum 的所有枚举值信息 | `UNiagaraToolset_Info` |

### 使用示例（蓝图描述）

**场景：AI 从零创建一个 Niagara 特效系统**

1. 调用 `FindNiagaraScripts` 搜索项目中可用的粒子模块资产
2. 调用 `CreateNiagaraSystem` 基于模板创建新系统
3. 调用 `AddEmitter` 向系统添加发射器
4. 调用 `AddModule` 向发射器的脚本堆栈添加模块
5. 调用 `SetStackInputData` 设置模块的输入参数值
6. 调用 `GetStackIssues` 检查是否有编译错误
7. 如有问题，调用 `ApplyStackIssueFix` 自动修复

**场景：AI 诊断并修复现有 Niagara 系统**

1. 调用 `GetSystemSummary` 获取系统概览
2. 调用 `GetEmitterTopology` 逐个查看发射器结构
3. 调用 `GetSystemCompileState` 获取编译状态
4. 调用 `GetStackIssues` 获取所有问题列表
5. 对每个问题调用 `ApplyStackIssueFix` 尝试自动修复

## C++ 用法

### 头文件引入

```cpp
#include "NiagaraToolset_System.h"
#include "NiagaraToolset_Assets.h"
#include "NiagaraToolset_Component.h"
#include "NiagaraToolset_Blueprint.h"
```

### 基本用法

以下示例展示了如何通过 C++ 调用 Niagara 工具集的核心功能：

```cpp
// 来源: Source/NiagaraToolsets/Private/NiagaraToolset_System.h

// 1. 创建 Niagara 系统
UNiagaraSystem* NewSystem = UNiagaraToolset_System::CreateNiagaraSystem(
    TEXT("MyEffect"),              // 资产名称
    TEXT("/Game/Effects"),         // 存储路径
    TemplateSystem                 // 模板系统
);

// 2. 获取系统摘要
FNiagaraExt_SystemSummary Summary = UNiagaraToolset_System::GetSystemSummary(NewSystem);

// 3. 添加发射器到系统
FNiagaraExt_EmitterTopology EmitterTopo = UNiagaraToolset_System::AddEmitter(
    NewSystem,
    TemplateEmitter,
    FName("SparkEmitter")
);

// 4. 添加模块到发射器的脚本堆栈
FNiagaraExt_ModuleReference ModuleRef; // 从拓扑中获取的引用
FNiagaraExt_ModuleTopology ModuleTopo = UNiagaraToolset_System::AddModule(
    ModuleLocationRef,    // 堆栈中的位置引用
    SpawnModuleAsset      // 模块脚本资产
);

// 5. 读写属性值
FNiagaraExt_SystemData SysData = UNiagaraToolset_System::GetSystemData(NewSystem);
// 修改后写回
UNiagaraToolset_System::SetSystemData(NewSystem, SysData);
```

### 进阶用法

**Schema 驱动的编辑流程** — 先查询 Schema 了解可设置的属性，再进行读写：

```cpp
// 来源: Source/NiagaraToolsets/Private/NiagaraToolset_System.h

// 获取渲染器 Schema，了解可配置的属性
FNiagaraExt_RendererSchema Schema = UNiagaraToolset_System::GetRendererSchema(
    UNiagaraSpriteRendererProperties::StaticClass()
);

// 获取当前渲染器数据
FNiagaraExt_RendererData RendererData = UNiagaraToolset_System::GetRendererData(RendererRef);

// 修改后写回
UNiagaraToolset_System::SetRendererData(RendererRef, RendererData);
```

**资产搜索与模块添加** — 搜索项目中的模块资产，然后添加到堆栈：

```cpp
// 来源: Source/NiagaraToolsets/Private/NiagaraToolset_Assets.h, NiagaraToolset_System.h

// 搜索粒子生成相关模块
TArray<FAssetData> Results = UNiagaraToolset_Assets::FindNiagaraScripts(
    TEXT("/Game/"),               // 搜索路径
    TEXT("Spawn"),                // 名称过滤
    { ENiagaraScriptUsage::Module }, // 只找模块
    { ENiagaraScriptLibraryVisibility::Library }, // 只找已公开的
    0,                           // 不按模块用途位掩码过滤
    true,                        // 递归搜索子目录
    false                        // 不包含已废弃的
);

// 获取模块的解码元数据
FNiagaraExt_ScriptDigest Digest = UNiagaraToolset_Assets::GetNiagaraScriptDigest(
    Results[0].GetSoftObjectPath().ToString()
);

// 查看模块 Schema
FNiagaraExt_ModuleSchema ModuleSchema = UNiagaraToolset_System::GetModuleSchemaFromAsset(
    Cast<UNiagaraScript>(Results[0].GetAsset())
);
```

**异步诊断与自动修复**：

```cpp
// 来源: Source/NiagaraToolsets/Private/NiagaraToolset_System.h

// 获取编译状态（异步）
UNiagaraToolset_AsyncSystemCompileState* CompileState = 
    UNiagaraToolset_System::GetSystemCompileState(System);
// 等待完成，然后读取 CompileState->Value

// 获取堆栈问题（异步）
UNiagaraToolset_AsyncStackIssues* Issues = 
    UNiagaraToolset_System::GetStackIssues(System);

// 应用修复（异步，会等待重新编译完成）
UNiagaraToolset_AsyncApplyStackIssueFixResult* FixResult = 
    UNiagaraToolset_System::ApplyStackIssueFix(System, IssueId, FixId);
// FixResult->Value.ApplyResult 包含修复结果
// FixResult->Value.PostFixIssues 包含修复后的堆栈状态
```

## Demo 示例

```cpp
// MyNiagaraToolsetExample.h
#pragma once

#include "CoreMinimal.h"

class FMyNiagaraToolsetExample
{
public:
    static void CreateSimpleEffect(UWorld* World);
    static void DiagnoseAndFixSystem(UNiagaraSystem* System);
};
```

```cpp
// MyNiagaraToolsetExample.cpp
#include "MyNiagaraToolsetExample.h"

#include "NiagaraToolset_System.h"
#include "NiagaraToolset_Assets.h"
#include "NiagaraToolset_Component.h"

void FMyNiagaraToolsetExample::CreateSimpleEffect(UWorld* World)
{
    // 1. 在项目中搜索可用的 Niagara 模块
    TArray<FAssetData> Modules = UNiagaraToolset_Assets::FindNiagaraScripts(
        TEXT("/Game/"), TEXT(""), {}, {}, 0, true, false
    );
    
    UE_LOG(LogTemp, Log, TEXT("Found %d Niagara scripts in project"), Modules.Num());

    // 2. 获取任意一个系统摘要作为示例（实际场景中会从资产加载）
    // 此处假设已有 System 对象
    UNiagaraSystem* System = nullptr; // 需要实际的系统对象
    if (!System) return;
    
    FNiagaraExt_SystemSummary Summary = UNiagaraToolset_System::GetSystemSummary(System);
    UE_LOG(LogTemp, Log, TEXT("System has %d emitters"), Summary.EmitterSummaries.Num());

    // 3. 遍历发射器拓扑
    for (const auto& EmitterSummary : Summary.EmitterSummaries)
    {
        FNiagaraExt_EmitterTopology Topo = UNiagaraToolset_System::GetEmitterTopology(
            EmitterSummary.EmitterRef
        );
        
        // 4. 获取所有模块的输入值
        TArray<FNiagaraExt_ModuleInputValues> InputValues = 
            UNiagaraToolset_System::GetEmitterInputValues(EmitterSummary.EmitterRef);
    }
}

void FMyNiagaraToolsetExample::DiagnoseAndFixSystem(UNiagaraSystem* System)
{
    if (!System) return;
    
    // 获取编译状态
    UNiagaraToolset_AsyncSystemCompileState* CompileResult = 
        UNiagaraToolset_System::GetSystemCompileState(System);
    
    // 获取所有堆栈问题
    UNiagaraToolset_AsyncStackIssues* StackIssues = 
        UNiagaraToolset_System::GetStackIssues(System);
    
    // 获取系统依赖
    FNiagaraExt_SystemDependencies Deps = 
        UNiagaraToolset_System::GetSystemDependencies(System);
    
    UE_LOG(LogTemp, Log, TEXT("System uses %d renderers, %d data interfaces, %d modules, %d dynamic inputs"),
        Deps.UsedRenderers.Num(), Deps.UsedDataInterfaces.Num(),
        Deps.UsedModules.Num(), Deps.UsedDynamicInputs.Num());
}
```

## 模块依赖

该插件依赖以下 UE 插件：

| 插件 | 用途 |
|---|---|
| `Niagara` | Niagara 粒子系统核心插件，提供所有 Niagara 类型和运行时 |
| `ToolsetRegistry` | AI 工具集注册框架，提供 `UToolsetDefinition` 基类和 JSON 转换器接口 |

无特殊模块依赖（仅标准 Editor/Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a73fd57f` | [bug-fix] UE-377457: Niagara property-write failures now nudge the caller toward the property schema | 修复属性写入失败时引导调用者查看属性 Schema |
| 2026-05-12 | `8b443338` | Fix a crash where the FToolsetReferenceConverter cannot find the correct Outer to create a new insta | 修复 FToolsetReferenceConverter 创建实例时找不到正确 Outer 导致的崩溃 |
| 2026-05-12 | `439fde12` | Converted Niagara skills from C++ classes to Python classes as the C++ classes were causing issues w | 将 Niagara 技能从 C++ 类迁移到 Python 类以解决兼容性问题 |
| 2026-05-12 | `0cff5168` | Niagara Toolset Skills: General skill set based on common procedures found. | 添加基于常见流程的通用技能集 |
| 2026-05-12 | `4312f802` | Niagara Assets Toolset: Added FindNiagaraScript tool. Moved the GetAssetDiscoveryInfo tool into this | 资产工具集新增 FindNiagaraScript，将 GetAssetDiscoveryInfo 移入资产工具集 |

### 维护评价

- **创建时间**：2026-04-23，非常新的插件
- **活跃度**：近期（2026-05-12~14）有密集的功能迭代和 bug 修复，处于活跃开发期
- **状态**：实验性插件（`IsExperimentalVersion: true`），默认禁用
- **已知限制**：
  - 实验性 API，接口可能随版本变化
  - 仅在编辑器中可用，不支持运行时
  - 部分功能依赖异步操作（编译状态、堆栈问题）
- **推荐**：如果你正在开发 AI 辅助的 Niagara 内容创建工作流，这是官方推荐的基础设施。但由于是实验性插件，生产环境使用需谨慎，建议持续关注 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/NiagaraToolsets)
- 官方文档（无）