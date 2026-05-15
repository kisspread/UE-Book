# Toolset Registry

> 

| 属性 | 值 |
|---|---|
| 中文名 | 工具集注册表 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ToolsetRegistry` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026‑01‑28 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolsetRegistry) | |

---

## 用途

`ToolsetRegistry` 提供一个**集中注册和发现机制**，用于管理 AI 工具集（Toolset）与单个工具（Tool）。  
它的核心设计目标是：

1. **解耦**：将工具集管理逻辑从 `AIAssistant` 插件中抽出，使得第三方库只需依赖 `ToolsetRegistry` 即可提供可被 AI 调用的工具，而不必引入 AI 助理的庞大依赖树。
2. **标准化工具描述**：通过 JSON Schema 自动生成每个工具的输入参数与返回值的结构描述，方便 AI 代理理解如何调用。
3. **灵活过滤**：支持通过“块名单/允许名单”模式（支持正则表达式）动态启用/禁用工具集或单个工具。
4. **异步支持**：工具执行返回 `TFuture` 或 Blueprint‑可用的 `UToolCallAsyncResult`，支持 UI 不卡顿的长时间操作。
5. **扩展性**：提供 `FToolsetJsonConverter` 基类，允许注册自定义属性类型与 JSON 的双向转换（如 `FTransform`、`FGuid`、`UObject` 引用等）。
6. **Agent Skill 管理**：内置 `AgentSkill` 概念，允许 AI 创建/更新/列举知识点级别的技能。

---

## 使用场景

- 你正在开发一个**AI 辅助编辑器插件**（如代码生成、材质助手），需要提供一组可被 LLM 调用的工具集。
- 你希望**将工具集与 AI 聊天界面分离**，使工具集库本身不依赖任何对话系统。
- 你需要**精细控制哪些工具暴露给 AI**（例如在编辑器模式下隐藏某些破坏性工具）。
- 你需要在 C++ 或 Python 中**自动发现和执行编辑器中的“函数库”工具**（使用 `UToolsetDefinition` 标记的静态函数）。

---

## 蓝图用法

### 核心节点

所有 BlueprintCallable 函数均为静态方法，分为以下几组。

#### 1. 工具集注册与执行

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsAvailable` | 检查工具集注册表是否可用（编辑器是否就绪） | `UToolsetRegistry` |
| `RegisterToolsetClass` | 注册一个继承自 `UToolsetDefinition` 的蓝图类作为工具集 | `UToolsetRegistry` |
| `UnregisterToolsetClass` | 注销已注册的工具集类 | `UToolsetRegistry` |
| `IsToolsetClassRegistered` | 查询是否已注册 | `UToolsetRegistry` |
| `IsToolsetRegistered` | 按名称查询是否已注册 | `UToolsetRegistry` |
| `ExecuteTool` | 执行指定工具集下的工具，返回异步结果 | `UToolsetRegistry` |
| `GetToolsetJsonSchema` | 获取单个工具集的 JSON Schema | `UToolsetRegistry` |
| `GetAllToolsetJsonSchemas` | 获取所有注册工具集的 JSON Schema | `UToolsetRegistry` |

#### 2. 反射辅助工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListStructProperties` | 将结构体的属性以 JSON Schema 字符串形式返回 | `UToolsetLibrary` |
| `GetObjectProperties` | 按属性名读取对象的多个属性值，返回 JSON 字符串 | `UToolsetLibrary` |
| `SetObjectProperties` | 从 JSON 字符串批量设置对象的属性，支持容器变更通知 | `UToolsetLibrary` |
| `GetDerivedClasses` | 获取某 UClass 的所有子类（原生 + 蓝图） | `UToolsetLibrary` |
| `GetDerivedStructs` | 获取某 UScriptStruct 的所有派生结构体 | `UToolsetLibrary` |
| `UndoTransaction` | 撤销最近一次事务（配合 BeginTransaction 使用） | `UToolsetLibrary` |

#### 3. Agent Skill 管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListSkills` | 列出项目中所有 AgentSkill（返回路径→描述映射） | `UAgentSkillToolset` |
| `GetSkills` | 获取多个技能的详细信息 | `UAgentSkillToolset` |
| `CreateSkill` | 创建新的 AgentSkill 资产 | `UAgentSkillToolset` |
| `UpdateSkill` | 更新已有 AgentSkill 的内容 | `UAgentSkillToolset` |

#### 4. 异步结果类型

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetValueAsJsonString` | 获取异步结果中的 JSON 值字符串（已完成时） | `UToolCallAsyncResult` |
| `SetError` | 手动标记异步结果为错误 | `UToolCallAsyncResult` |
| `BroadcastOnCompletedIfComplete` | 如果结果已经完成，触发 `OnCompleted` 回调 | `UToolCallAsyncResult` |
| `SetValue` (子类) | 设置结果值并标记完成（`UToolCallAsyncResultString` / `UToolCallAsyncResultImage`） | 具体子类 |
| `SetCompleted` (Void) | 无返回值的完成 | `UToolCallAsyncResultVoid` |

#### 5. Python 测试运行器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create` | 创建 Python 测试运行器实例（通常在 `init_unreal.py` 中使用） | `UPythonTestRunner` |
| `GetTests` | 获取发现的测试 ID 列表 | `UPythonTestRunner` |
| `RunTest` | 运行指定 ID 的测试 | `UPythonTestRunner` |
| `GetLastTestResult` | 获取某次测试的最新结果 | `UPythonTestRunner` |

### 使用示例（蓝图描述）

**注册工具集并执行工具：**
1. 创建一个继承自 `UToolsetDefinition` 的蓝图类，命名为 `BP_MyTools`。在蓝图图表中添加一个静态函数（`meta = (AICallable)`），例如 `GreetPlayer(Name: String) -> String`。
2. 在关卡蓝图（或编辑器脚本）中调用 `RegisterToolsetClass`，目标选 `BP_MyTools`。
3. 调用 `ExecuteTool`，输入 ToolsetName（蓝图类名称）、ToolName（静态函数名）、JsonInput（如 `{"name": "John"}`）。返回的 `UToolCallAsyncResultString` 绑定 `OnCompleted` 事件，从 `Value` 引脚读取结果。

**读取对象属性：**
1. 调用 `GetObjectProperties`，输入目标对象引用和属性名数组。输出 JSON 字符串，可解析后使用。

---

## C++ 用法

### 头文件引入

```cpp
#include "ToolsetRegistry/ToolsetRegistry.h"
#include "ToolsetRegistry/ToolsetRegistrySubsystem.h"
#include "ToolsetRegistry/ToolsetLibrary.h"
#include "ToolsetRegistry/UToolsetRegistry.h"
```

### 基本用法

#### 1. 获取子系统并注册工具集

```cpp
// 获取 UToolsetRegistrySubsystem（EditorSubsystem，仅编辑器可用）
auto Subsystem = GEditor->GetEditorSubsystem<UToolsetRegistrySubsystem>();
if (Subsystem)
{
    UE::ToolsetRegistry::FToolsetRegistry& Registry = Subsystem->ToolsetRegistry;

    // 注册一个 C++ 实现的工具集（需继承 FToolset）
    TSharedPtr<UE::ToolsetRegistry::FToolset> MyToolset = MakeShared<FMyToolset>();
    Registry.RegisterToolset(MyToolset);
}
```

#### 2. 通过 UToolsetDefinition 注册蓝图工具集

```cpp
UToolsetRegistry::RegisterToolsetClass(SomeBlueprintToolsetClass);
// 内部会创建 FFunctionLibraryToolset 并加入 Registry
```

#### 3. 执行工具

```cpp
TFuture<TValueOrError<FString, FString>> ResultFuture =
    Registry.ExecuteTool(TEXT("MyToolset"), TEXT("GreetPlayer"), TEXT(R"({"name":"John"})"));

// 等待完成（可使用 .Then 或同步 Wait）
ResultFuture.Wait();
TValueOrError<FString, FString> Result = ResultFuture.Get();
if (Result.HasValue())
{
    UE_LOG(LogTemp, Log, TEXT("Result: %s"), *Result.GetValue());
}
else
{
    UE_LOG(LogTemp, Error, TEXT("Error: %s"), *Result.GetError());
}
```

#### 4. 批量设置属性（带动画通知）

```cpp
UToolsetLibrary::SetObjectProperties(
    SomeObject,
    TEXT(R"({"Location":{"X":100,"Y":0,"Z":50}})"),
    EBypassContainerCheck::No
);
// 内部会对比容器变化并触发正确的 ArrayAdd/ValueSet 等通知
```

### 进阶用法

#### 自定义 JSON 转换器

假设你想将 `FDouble` 类型按特殊格式序列化，可继承 `FToolsetJsonConverter`：

```cpp
class FMyDoubleConverter : public UE::ToolsetRegistry::FToolsetJsonConverter
{
    virtual FString GetName() const override { return TEXT("MyDoubleConverter"); }
    virtual bool CanConvertProperty(TNotNull<const FProperty*> Property) override
    {
        return Property->GetCPPType() == TEXT("double");
    }
    // ... 实现其余纯虚函数
};

// 注册
auto Converter = MakeShared<FMyDoubleConverter>();
Registry.RegisterConverter(Converter);
```

#### 使用块名单过滤

```cpp
// 块名单：禁用所有以 "Test" 开头的工具集
Registry.AddBlockedName(TEXT("/^Test.*/"));

// 允许名单：只允许 "CoreTools" 和 "EditorTools" 两个工具集
Registry.AddAllowedName(TEXT("CoreTools"));
Registry.AddAllowedName(TEXT("EditorTools"));
// 注意：块名单优先
```

#### 异步结果处理（C++）

```cpp
UToolCallAsyncResultString* ResultObj = NewObject<UToolCallAsyncResultString>();
ResultObj->OnCompleted.AddLambda([ResultObj]()
{
    if (ResultObj->bIsComplete && ResultObj->Error.IsEmpty())
    {
        FString JsonValue = ResultObj->Value;
        // 处理成功的 JSON 值
    }
    else
    {
        FString Error = ResultObj->Error;
        // 处理错误
    }
});

// 如果结果已经完成（例如同步完成），需要手动广播
if (!ResultObj->BroadcastOnCompletedIfComplete())
{
    // 尚未完成，等待异步完成信号
}
```

---

## Demo 示例

以下是一个最小 C++ 工具集实现，注册并执行一个简单的“加法”工具。

**头文件 `MyMathToolset.h`**  
```cpp
#pragma once
#include "ToolsetRegistry/Toolset.h"
#include "ToolsetRegistry/ToolsetRegistrySubsystem.h"
#include "ToolsetRegistry/ValueOrErrorFuture.h" // Internal

class FMyMathToolset : public UE::ToolsetRegistry::FToolset
{
public:
    virtual FString GetToolsetName() const override { return TEXT("MathTools"); }
    virtual FString GetToolsetVersion() const override { return TEXT("1.0"); }
    virtual FString GetToolsetDescription() const override { return TEXT("Simple math operations"); }

protected:
    virtual TFuture<TValueOrError<FString, FString>> ExecuteToolInternal(
        const FString& ToolName, const FString& JsonInput) override
    {
        if (ToolName == TEXT("Add"))
        {
            // 解析 JSON 输入
            TSharedPtr<FJsonObject> JsonObj;
            TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonInput);
            if (!FJsonSerializer::Deserialize(Reader, JsonObj) || !JsonObj.IsValid())
            {
                return UE::ToolsetRegistry::Internal::FStringValueOrErrorFuture::MakeError(
                    TEXT("Invalid JSON"));
            }
            double A = JsonObj->GetNumberField("a");
            double B = JsonObj->GetNumberField("b");
            double Result = A + B;

            // 构造返回 JSON
            TSharedPtr<FJsonObject> OutObj = MakeShared<FJsonObject>();
            OutObj->SetNumberField("sum", Result);
            FString OutString;
            TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&OutString);
            FJsonSerializer::Serialize(OutObj.ToSharedRef(), Writer);

            return UE::ToolsetRegistry::Internal::FStringValueOrErrorFuture::MakeValue(
                MoveTemp(OutString));
        }
        return UE::ToolsetRegistry::Internal::FStringValueOrErrorFuture::MakeError(
            FString::Printf(TEXT("Unknown tool: %s"), *ToolName));
    }

    virtual FString GetJsonSchemaInternal() const override
    {
        // 返回一个简单的 JSON Schema 描述此工具集的工具
        // 实际项目中可通过 ToolsetJson 工具链自动生成
        return TEXT(R"([{"name":"Add","description":"Add two numbers","parameters":{"type":"object","properties":{"a":{"type":"number"},"b":{"type":"number"}},"required":["a","b"]}}])");
    }
};
```

**.cpp 文件（注册）**  
```cpp
#include "MyMathToolset.h"
#include "ToolsetRegistry/ToolsetRegistrySubsystem.h"

void RegisterMyToolset()
{
    if (UToolsetRegistrySubsystem* Subsystem = GEditor->GetEditorSubsystem<UToolsetRegistrySubsystem>())
    {
        TSharedPtr<FMyMathToolset> MathToolset = MakeShared<FMyMathToolset>();
        Subsystem->ToolsetRegistry.RegisterToolset(MathToolset);
    }
}
```

在编辑器启动时（例如 `StartupModule`）调用 `RegisterMyToolset()`，即可在 Python 或蓝图中通过 `ExecuteTool("MathTools", "Add", ...)` 使用。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PythonScriptPlugin` | 提供 Python 支持，用于 Python 测试运行器及脚本执行 |
| `EditorScriptingUtilities` | 提供编辑器脚本相关的实用函数（如资产操作） |
| `FileSandbox` | 提供文件沙箱功能，用于安全地测试文件系统操作（见 `FSandboxLibrary`） |

> **说明**：`ToolsetRegistry` 本身是一个 Editor 模块，因此也隐含依赖 `UnrealEd`、`Settings` 等常见依赖，但不在此重复列出。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026‑05‑14 | `a6b716df` | Block list for UToolsetLibrary::SetObjectProperties | 为 `SetObjectProperties` 添加基于类/属性的黑名单过滤，防止 AI 修改受保护的属性 |
| 2026‑05‑14 | `3e643253` | Wrap execute_tool_script in a transaction with automatic rollback on error | 将工具脚本执行包裹在事务中，出错时自动撤销修改，避免留下脏数据 |
| 2026‑05‑14 | `02299b89` | [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties | 修复 `SetObjectProperties` 对数组/容器属性的变更通知，正确触发 `ArrayAdd`/`ArrayRemove` 等事件 |
| 2026‑05‑14 | `fc9371a0` | Drop redundant UE_LOGF in OnScriptException | 移除 `OnScriptException` 中的冗余日志，减少输出噪声 |
| 2026‑05‑13 | `978a5c16` | [Backout] - CL53875137 | 回退某个有问题的提交（CL53875137） |

### 维护评价

- **创建时间**：2026‑01‑28，距今约 **4 个月**，仍属于非常年轻的插件。
- **近期活跃度**：最近一个月（2026‑05）有密集的功能性更新：添加黑名单、事务回滚、容器通知修复。说明正在积极开发中。
- **已知问题**：部分功能仍处于实验阶段，例如 `SetObjectProperties` 的容器通知逻辑在近期才完成，可能存在边缘情况。
- **推荐程度**：**推荐在开发环境中使用**。如果你正在构建 AI 驱动的编辑器工具，`ToolsetRegistry` 是最佳的基础设施选择。它独立于 `AIAssistant`，轻量且可扩展。需要注意的是，它是一个**实验性插件**，默认未启用，需要在插件管理器中手动开启。由于其 API 仍在快速演进，请关注每次引擎更新的兼容性。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolsetRegistry)
- 官方文档：暂无（`DocsURL` 为空）
- 测试用例：位于源码仓库 `Engine/Plugins/Experimental/ToolsetRegistry/Tests` 目录及 `Engine/Tests` 中的 `AI.ToolsetRegistry` 分类。