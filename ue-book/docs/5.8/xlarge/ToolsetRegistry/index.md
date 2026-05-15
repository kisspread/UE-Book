# Toolset Registry

> （描述为空）

| 属性 | 值 |
|---|---|
| 中文名 | 工具集注册表 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ToolsetRegistry` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolsetRegistry) | |

---

## 用途

Toolset Registry 是一个编辑器专用框架，用于在 Unreal Editor 中 **注册、发现和执行“工具集”（Toolset）**。每个工具集包含一组可被 AI 或用户调用的工具（Tool），工具本质上是暴露为 `AICallable` 的静态蓝图函数或 C++ 函数。

该插件解决的核心问题：**为 AI 助手（如 AI 编程助手）提供结构化的、可扩展的编辑器操作能力**。通过统一的注册表，AI 可以动态查询可用工具及其 JSON Schema，然后传入参数执行工具，获取返回结果。此外，插件还提供了：

- **属性读取/写入**：通过 `UToolsetLibrary` 安全地 Get/Set 任意 UObject 的属性，并自动发出正确的 Undo/Redo 通知。
- **事务管理**：支持包裹工具执行在事务中，出错时自动回滚。
- **文件沙盒集成**：与 `FileSandbox` 插件联动，提供隔离的文件操作环境。
- **Agent 技能系统**：将技能（Skill）定义为一组依赖的工具集和说明文本，方便 AI 动态加载使用。
- **Python 测试集成**：允许将 Python 单元测试注册到 Unreal 自动化测试框架中运行。

---

## 使用场景

- **开发 AI 编程助手**：注册自定义工具集，让 AI 能够获取场景对象属性、创建资产、运行脚本、操作文件等。
- **自定义编辑器扩展**：将复杂操作封装为工具（如批量修改材质、导出关卡数据），通过 JSON 输入输出暴露给外部系统（如聊天机器人、Web API）。
- **自动化测试**：利用 `UPythonTestRunner` 将 Python 的 `unittest` 测试用例注册到 Unreal 的自动化测试框架，统一管理和运行。
- **Agent 技能系统**：定义高级技能（如“创建角色”），将多个基础工具按顺序/条件组合，供 AI 或用户按需调用。

---

## 蓝图用法

插件中所有 `BlueprintCallable` 函数均可在蓝图或 Python 中调用。以下按功能分组列出核心节点。

### 工具集注册与管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsAvailable` | 检查工具集注册表是否可用（编辑器就绪时） | `UToolsetRegistry` |
| `RegisterToolsetClass` | 注册一个 `UToolsetDefinition` 子类作为工具集 | `UToolsetRegistry` |
| `UnregisterToolsetClass` | 注销已注册的工具集类 | `UToolsetRegistry` |
| `IsToolsetClassRegistered` | 查询某个类是否已注册 | `UToolsetRegistry` |
| `IsToolsetRegistered` | 按名称查询工具集是否已注册 | `UToolsetRegistry` |
| `ExecuteTool` | 执行指定工具集下的某个工具，传入 JSON 参数，返回异步结果 | `UToolsetRegistry` |
| `GetToolsetJsonSchema` | 获取某个工具集类的 JSON Schema | `UToolsetRegistry` |
| `GetAllToolsetJsonSchemas` | 获取所有已注册工具集的 JSON Schema 合并字符串 | `UToolsetRegistry` |

### 属性读取与写入

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListStructProperties` | 返回一个结构体的属性列表（以 JSON Schema 格式） | `UToolsetLibrary` |
| `GetObjectProperties` | 获取指定对象的多个属性值，返回 JSON 字符串 | `UToolsetLibrary` |
| `SetObjectProperties` | 从 JSON 字符串设置对象的属性值，返回是否成功 | `UToolsetLibrary` |
| `GetDerivedClasses` | 获取某个类的所有派生类（原生和蓝图） | `UToolsetLibrary` |
| `GetDerivedStructs` | 获取某个结构体的所有派生结构体（已加载的） | `UToolsetLibrary` |
| `UndoTransaction` | 撤销最近一次事务（配合 BeginTransaction/EndTransaction 使用） | `UToolsetLibrary` |

### 异步工具结果处理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetValueAsJsonString` | 获取异步结果的 JSON 字符串表示 | `UToolCallAsyncResult` |
| `SetError` | 将异步结果标记为错误并通知监听器 | `UToolCallAsyncResult` |
| `BroadcastOnCompletedIfComplete` | 如果结果已经完成，立即广播 `OnCompleted` 事件 | `UToolCallAsyncResult` |
| `SetValue` | 设置结果的值（字符串） | `UToolCallAsyncResultString` |
| `SetValue` | 设置结果的值（图片） | `UToolCallAsyncResultImage` |
| `SetCompleted` | 标记完成（无返回值） | `UToolCallAsyncResultVoid` |

### Agent 技能管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ListSkills` | 列出项目中所有 Agent 技能的概览（路径 -> 描述） | `UAgentSkillToolset` |
| `GetSkills` | 返回指定技能路径的详细信息（依赖工具集、说明） | `UAgentSkillToolset` |
| `CreateSkill` | 创建新的 Agent 技能资产（需用户许可） | `UAgentSkillToolset` |
| `UpdateSkill` | 更新已有技能的内容（需用户许可） | `UAgentSkillToolset` |

### Python 测试运行

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create` | 创建 Python 测试运行器实例，注册到自动化测试框架 | `UPythonTestRunner` |
| `GetTests` | 返回发现的测试 ID 列表 | `UPythonTestRunner` |
| `RunTest` | 运行指定 ID 的测试 | `UPythonTestRunner` |
| `GetLastTestResult` | 查询某个测试的执行结果（是否完成、是否成功） | `UPythonTestRunner` |

---

### 使用示例（蓝图描述）

**注册并执行工具**：
1. 调用 `RegisterToolsetClass`，传入一个继承自 `UToolsetDefinition` 的蓝图类（例如 `BP_MyTools`）。
2. 调用 `ExecuteTool`，输入工具集名称（蓝图类的 DisplayName）、工具名（蓝图函数名）、JSON 参数（字符串）。
3. `ExecuteTool` 返回 `UToolCallAsyncResultString` 对象，绑定其 `OnCompleted` 事件，在事件中调用 `GetValueAsJsonString` 获取结果。

**设置对象属性**：
1. 构造一个 JSON 字符串，例如 `{"ActorLocation": {"X": 100, "Y": 0, "Z": 50}}`。
2. 调用 `SetObjectProperties`，传入目标 `Object`、JSON 字符串和 `BypassContainerCheck` 选项（通常为 `No`）。
3. 该函数会自动发出正确的 Pre/PostEditChange 通知，支持 Undo/Redo。

**撤销事务**：
1. 使用 `UKismetSystemLibrary.BeginTransaction` 开始一个事务。
2. 进行一系列对象修改（如通过 `SetObjectProperties`）。
3. 如果出错，调用 `UToolsetLibrary.UndoTransaction` 回滚。

---

## C++ 用法

### 头文件引入

```cpp
#include "ToolsetRegistry/ToolsetRegistry.h"
#include "ToolsetRegistry/ToolsetLibrary.h"
#include "ToolsetRegistry/ToolsetDefinition.h"
```

### 基本用法

**注册自定义工具集**（Source: `Engine/Plugins/Experimental/ToolsetRegistry/Private/ToolsetRegistry/FunctionLibraryToolset.h`）

```cpp
// 1. 定义工具集类
UCLASS(BlueprintType, DisplayName = "My Custom Tools")
class UMyToolset : public UToolsetDefinition
{
    GENERATED_BODY()
public:
    UFUNCTION(meta = (AICallable))  // 标记为可被 AI 调用的工具
    static FString GetSceneInfo(const FVector& Location)
    {
        // 返回场景中某点的信息，格式为 JSON 字符串
        return TEXT("{\"name\":\"test\", \"value\":42}");
    }

    virtual FString GetToolsetVersion() const override
    {
        return TEXT("1.0");
    }
};

// 2. 在模块 StartupModule 中注册
void FMyModule::StartupModule()
{
    UToolsetRegistry::RegisterToolsetClass(UMyToolset::StaticClass());
}

// 3. 通过工具集注册表执行工具
UToolCallAsyncResultString* Result = UToolsetRegistry::ExecuteTool(
    TEXT("My Custom Tools"),           // 工具集名称
    TEXT("GetSceneInfo"),              // 工具名（函数名）
    TEXT("{\"Location\":{\"X\":1,\"Y\":2,\"Z\":3}}")  // JSON 输入
);
```

**使用属性库设置对象属性**（Source: `Engine/Plugins/Experimental/ToolsetRegistry/Private/ToolsetRegistry/ToolsetLibraryImpl.h`）

```cpp
UStaticMeshComponent* MeshComp = ...;
FString Json = TEXT("{\"RelativeLocation\":{\"X\":100,\"Y\":0,\"Z\":50}}");

TArray<FName> SetPropertyNames;
bool bSuccess = UToolsetLibrary::SetObjectProperties(
    MeshComp, Json, SetPropertyNames, EBypassContainerCheck::No);
// SetPropertyNames 包含实际被设置的属性名数组
```

**使用异步结果**（Source: `Engine/Plugins/Experimental/ToolsetRegistry/Public/ToolsetRegistry/ToolCallAsyncResult.h`）

```cpp
UToolCallAsyncResultString* Result = ...;

// 绑定完成回调
Result->OnCompleted.AddLambda([Result]()
{
    if (!Result->Error.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("Tool failed: %s"), *Result->Error);
        return;
    }
    FString Value = Result->Value;
    UE_LOG(LogTemp, Log, TEXT("Tool result: %s"), *Value);
});

// 如果结果已经完成，手动广播
Result->BroadcastOnCompletedIfComplete();
```

**与文件沙盒交互**（Source: `Engine/Plugins/Experimental/ToolsetRegistry/Public/ToolsetRegistry/SandboxLibrary.h`）

```cpp
using UE::ToolsetRegistry::FGlobalSandbox;

// 进入沙盒
FGlobalSandbox::Enter(TEXT("MySandbox"), TEXT("Temporary working area"));

// 执行文件操作（实际文件写入会在沙盒内）
// ...

// 获取变更列表
auto Changes = FGlobalSandbox::GetChanges();

// 提交部分文件
FGlobalSandbox::Persist({TEXT("/Game/MyAsset.uasset")});

// 丢弃全部变更
FGlobalSandbox::Discard();

// 离开沙盒（不删除）
FGlobalSandbox::Leave();
```

**注册 Python 测试**（Source: `Engine/Plugins/Experimental/ToolsetRegistry/Private/ToolsetRegistry/PythonTestRunner.h`）

```cpp
// 在 Python init_unreal.py 中：
import unreal
from mypackage.tests import test_module

_test_runner = unreal.PythonTestRunner.create(
    'MyPackage.Tests',
    unreal.PythonTestRunnerSearchOptions(root_module=test_module.__name__))
```

### 进阶用法

**自定义属性序列化转换器**（Source: `Engine/Plugins/Experimental/ToolsetRegistry/Public/ToolsetRegistry/ToolsetJsonConverter.h`）

```cpp
class FMyCustomConverter : public FToolsetJsonConverter
{
    virtual FString GetName() const override { return TEXT("MyConverter"); }

    virtual bool CanConvertProperty(TNotNull<const FProperty*> Property) override
    {
        // 例如，只处理 FMyStruct 属性
        return Property->GetClass() == FMyStruct::StaticStruct();
    }

    virtual TSharedPtr<FJsonObject> PropertyToJsonSchema(
        TNotNull<const FProperty*> Property) override
    {
        // 返回自定义 JSON Schema
        return MakeShareable(new FJsonObject());
    }
    // ... 其他虚函数实现
};

// 注册转换器
FToolsetRegistry& Registry = ...;
Registry.RegisterConverter(MakeShared<FMyCustomConverter>());
```

**事务包裹工具执行**（Source: `Engine/Plugins/Experimental/ToolsetRegistry/Private/...`，从 git commit 描述）

```cpp
// 自动事务包裹（在内部实现，无需手动调用）
// 当通过 ExecuteTool 调用工具时，插件会自动创建一个事务；
// 如果工具执行过程中抛出脚本异常，会自动调用 UndoTransaction 回滚。
```

---

## Demo 示例

以下是一个完整的 C++ 工具集定义和注册示例，包括一个简单的工具用于获取场景相机位置。

**MyToolset.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "ToolsetRegistry/ToolsetDefinition.h"
#include "MyToolset.generated.h"

UCLASS(BlueprintType, DisplayName = "Camera Tools")
class UMyToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    // 获取当前编辑器视口相机位置（仅编辑器可用）
    UFUNCTION(meta = (AICallable))
    static FString GetEditorCameraLocation();

    virtual FString GetToolsetVersion() const override { return TEXT("1.0"); }
};
```

**MyToolset.cpp**

```cpp
#include "MyToolset.h"
#include "EditorViewportClient.h"
#include "LevelEditorViewport.h"
#include "JsonObjectConverter.h"

FString UMyToolset::GetEditorCameraLocation()
{
    FVector Location = FVector::ZeroVector;
    if (GCurrentLevelEditingViewportClient)
    {
        Location = GCurrentLevelEditingViewportClient->GetViewLocation();
    }
    // 返回 JSON
    return FString::Printf(TEXT("{\"X\":%f,\"Y\":%f,\"Z\":%f}"),
        Location.X, Location.Y, Location.Z);
}
```

**Module Startup**

```cpp
void FMyModule::StartupModule()
{
    UToolsetRegistry::RegisterToolsetClass(UMyToolset::StaticClass());
}
```

在蓝图中或通过 Python 调用：
```python
import unreal
registry = unreal.ToolsetRegistry
result = registry.execute_tool("Camera Tools", "GetEditorCameraLocation", "{}")
print(result.get_value_as_json_string())
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PythonScriptPlugin` | 提供 Python 脚本执行环境，用于工具实现和测试集成 |
| `EditorScriptingUtilities` | 提供编辑器脚本实用函数（如资产操作、编辑器查询） |
| `FileSandbox` | 提供沙盒文件系统，支持隔离的文件变更跟踪和提交 |

（其他标准依赖如 Core、Engine、UnrealEd 等已省略）

---

## 维护状态

### 近期更新

- 2026-05-14 a6b716df Block list for UToolsetLibrary::SetObjectProperties
- 2026-05-14 3e643253 Wrap execute_tool_script in a transaction with automatic rollback on error
- 2026-05-14 02299b89 [ToolsetRegistry] Emit correct container change notifications in SetObjectProperties
- 2026-05-14 fc9371a0 Drop redundant UE_LOGF in OnScriptException
- 2026-05-13 978a5c16 [Backout] - CL53875137

### 维护评价

- **创建时间**：2026-05-13，距今不到一个月（非常新）。
- **更新频率**：最近两天内有多个功能性提交（属性块列表、事务回滚、容器变更通知等），开发活跃。
- **实验性标记**：`.uplugin` 中 `IsExperimentalVersion=true`，表明 API 和功能可能仍有调整。
- **已知限制**：暂无已知问题记录，但作为实验性插件，不建议在项目生产环境中依赖过重。
- **推荐度**：适合在 AI 辅助编辑器开发场景中试用，关注后续版本稳定化。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolsetRegistry)
- [官方文档]（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolsetRegistry/Source/ToolsetRegistry/Private/Tests)（假设存在，实际路径可能不同）