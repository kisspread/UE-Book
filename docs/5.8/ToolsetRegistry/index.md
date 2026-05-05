# Toolset Registry

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `ToolsetRegistry` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-24 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolsetRegistry) | |

## 用途

ToolsetRegistry 是一个实验性的编辑器插件，旨在为 AI 助手（如基于大语言模型的代理）提供一个结构化的方式来发现和调用 Unreal Engine 编辑器中的工具。它解决的核心问题是：如何让 AI 安全、可控地与复杂的 UE 编辑器环境进行交互。

插件通过一个注册表（Registry）机制，允许开发者将各种“工具集”（Toolset）注册到系统中。每个工具集定义了一组相关的工具（例如，创建资产、修改场景、运行测试）。AI 助手可以通过查询注册表获取所有可用工具的 JSON Schema 描述，从而了解每个工具需要什么输入参数以及会返回什么输出。随后，AI 可以通过 JSON 格式的输入来调用这些工具，并接收 JSON 格式的输出或错误信息。

简而言之，它为 AI 代理与 UE 编辑器之间搭建了一座标准化的“工具调用”桥梁。

## 使用场景

- **AI 驱动的编辑器自动化**：你正在开发一个 AI 助手，希望它能自动执行诸如“在场景中放置一个立方体”、“创建一个新的材质并设置其颜色”、“查找所有未使用的纹理资产”等任务。
- **构建自定义 AI 工作流**：你需要将特定的编辑器功能（例如，你的游戏项目特有的资产处理流程）暴露给 AI，以便通过自然语言指令进行控制。
- **测试 AI 工具调用**：在开发 AI 代理时，你需要一个标准化的环境来测试工具调用的正确性和鲁棒性。

## 蓝图用法

该插件主要通过蓝图函数库 `UToolsetRegistry` 和 `UToolsetLibrary` 提供蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterToolsetClass` | 将一个 `UToolsetDefinition` 的子类注册为工具集。 | `UToolsetRegistry` |
| `UnregisterToolsetClass` | 注销一个已注册的工具集类。 | `UToolsetRegistry` |
| `IsToolsetClassRegistered` | 检查一个工具集类是否已注册。 | `UToolsetRegistry` |
| `ExecuteTool` | 通过工具集名称和工具名称执行一个已注册的工具。主要用于测试。 | `UToolsetRegistry` |
| `GetAllToolsetJsonSchemas` | 获取所有已注册工具集的 JSON Schema 描述。 | `UToolsetRegistry` |
| `ListStructProperties` | 将一个 UStruct 的属性以 JSON Schema 格式返回。 | `UToolsetLibrary` |
| `GetObjectProperties` | 获取一个 UObject 上指定属性的值，以 JSON 字符串返回。 | `UToolsetLibrary` |
| `SetObjectProperties` | 通过 JSON 字符串设置一个 UObject 上的属性值。 | `UToolsetLibrary` |
| `GetDerivedClasses` | 获取一个基类的所有派生类（包括原生和蓝图类）。 | `UToolsetLibrary` |

### 使用示例（蓝图描述）

1.  **定义工具集**：创建一个继承自 `UToolsetDefinition` 的蓝图类。在该类中，创建静态函数，并使用 `meta=(AICallable)` 标记它们为可被 AI 调用的工具。函数的参数和返回值将被自动转换为 JSON Schema。
2.  **注册工具集**：在游戏初始化或编辑器启动时，调用 `UToolsetRegistry::RegisterToolsetClass` 节点，传入你定义的工具集蓝图类。
3.  **AI 查询与调用**：AI 助手（或测试蓝图）可以先调用 `GetAllToolsetJsonSchemas` 获取所有工具的描述，然后根据需要调用 `ExecuteTool`，传入工具集名称、工具名称和 JSON 格式的参数。

## C++ 用法

### 头文件引入

```cpp
#include "ToolsetRegistry/ToolsetRegistry.h"
#include "ToolsetRegistry/ToolsetDefinition.h"
#include "ToolsetRegistry/ToolsetLibrary.h"
```

### 基本用法

**定义一个 C++ 工具集** (来源: `Source/ToolsetRegistry/Private/Tests/FunctionLibraryToolsetTest.h`)

```cpp
// 继承自 UToolsetDefinition
UCLASS(Blueprintable, Hidden)
class UMyToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    // 定义一个可被 AI 调用的工具函数
    // meta=(AICallable) 是关键标记
    UFUNCTION(meta = (AICallable), Category = "MyTools")
    static FString CreateAsset(const FString& AssetName, const FString& AssetPath);

    // 标记为 AIIgnore 的函数不会被注册为工具
    UFUNCTION(meta = (AIIgnore))
    static void InternalHelperFunction();
};
```

**注册和调用工具** (来源: `Source/ToolsetRegistry/Private/Tests/ToolCallTestHelpers.h`)

```cpp
#include "ToolsetRegistry/ToolsetRegistrySubsystem.h"
#include "ToolsetRegistry/ObjectFunctionToolCall.h"

// 获取子系统
TValueOrError<TObjectPtr<UToolsetRegistrySubsystem>, FString> SubsystemResult = 
    UToolsetRegistrySubsystem::Get(TEXT("MyPlugin"));
if (SubsystemResult.HasValue())
{
    UToolsetRegistrySubsystem* Subsystem = SubsystemResult.GetValue();
    
    // 注册工具集类
    Subsystem->ToolsetRegistry.RegisterToolsetClass(UMyToolset::StaticClass());
    
    // 执行一个工具调用 (通常由 AI 代理完成)
    // 这里使用测试辅助函数模拟
    UObject* TestObject = GetDefault<UMyToolset>();
    UFunction* Function = TestObject->GetClass()->FindFunctionByName(TEXT("CreateAsset"));
    
    auto ToolCall = MakeShared<FObjectFunctionToolCall>(TestObject, Function);
    TFuture<FJsonValueOrError> ResultFuture = ToolCall->Execute(
        FObjectFunctionToolCall::FFunctionInputParamsJson(
            TInPlaceType<FString>(), 
            TEXT(R"({"AssetName": "MyNewAsset", "AssetPath": "/Game/Assets"}")")),
        MakeShared<FToolCallExceptionHandler>());
    
    // 处理结果
    FJsonValueOrError Result = ResultFuture.Get();
    if (Result.HasValue())
    {
        // 工具调用成功，Result.GetValue() 是返回的 JSON 值
    }
    else
    {
        // 工具调用失败，Result.GetError() 是错误信息
    }
}
```

### 进阶用法

**自定义 JSON 转换器** (来源: `Source/ToolsetRegistry/Private/Tests/FakeConverter.h`)

你可以继承 `FToolsetJsonConverter` 来处理自定义类型的 JSON 序列化/反序列化。

```cpp
class FMyCustomConverter : public UE::ToolsetRegistry::FToolsetJsonConverter
{
public:
    virtual FString GetName() const override { return TEXT("MyCustomConverter"); }
    
    virtual bool CanConvertProperty(TNotNull<const FProperty*> Property) override
    {
        // 判断此转换器是否能处理该属性类型
        return Property->IsA<FStructProperty>() && 
               CastField<FStructProperty>(Property)->Struct == FMyCustomStruct::StaticStruct();
    }
    
    // ... 实现其他虚函数，定义 FMyCustomStruct 与 JSON 的转换逻辑
};

// 注册转换器
Subsystem->ToolsetRegistry.RegisterConverter(MakeShared<FMyCustomConverter>());
```

**处理异步工具调用** (来源: `Source/ToolsetRegistry/Public/ToolsetRegistry/ToolCallAsyncResult.h`)

对于耗时操作，工具可以返回 `UToolCallAsyncResult` 的子类。

```cpp
UCLASS()
class UMyAsyncToolset : public UToolsetDefinition
{
    GENERATED_BODY()
public:
    UFUNCTION(meta = (AICallable), Category = "AsyncTools")
    static UToolCallAsyncResultString* LongRunningTask(const FString& Input);
};

// 在函数实现中
UToolCallAsyncResultString* UMyAsyncToolset::LongRunningTask(const FString& Input)
{
    UToolCallAsyncResultString* AsyncResult = NewObject<UToolCallAsyncResultString>();
    
    // 在后台线程执行任务
    Async(EExecutionThread::AnyBackgroundThreadNormalTask, [AsyncResult, Input]()
    {
        // ... 执行耗时操作 ...
        FString Result = DoWork(Input);
        
        // 回到游戏线程设置结果
        AsyncTask(ENamedThreads::GameThread, [AsyncResult, Result]()
        {
            AsyncResult->SetValue(Result); // 这将触发 OnCompleted 委托
        });
    });
    
    return AsyncResult;
}
```

## Demo 示例

一个最小的工具集定义和使用示例。

**MyToolset.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ToolsetRegistry/ToolsetDefinition.h"
#include "MyToolset.generated.h"

UCLASS(Blueprintable)
class UMyToolset : public UToolsetDefinition
{
    GENERATED_BODY()

public:
    // 一个简单的加法工具
    UFUNCTION(meta = (AICallable), Category = "Math")
    static int32 Add(int32 A, int32 B);
};
```

**MyToolset.cpp**
```cpp
#include "MyToolset.h"

int32 UMyToolset::Add(int32 A, int32 B)
{
    return A + B;
}
```

**使用 (在编辑器工具或测试中):**
```cpp
#include "MyToolset.h"
#include "ToolsetRegistry/ToolsetRegistrySubsystem.h"

void RegisterAndTestMyToolset()
{
    // 1. 获取子系统并注册
    auto SubsystemResult = UToolsetRegistrySubsystem::Get();
    if (SubsystemResult.HasError()) return;
    
    UToolsetRegistrySubsystem* Subsystem = SubsystemResult.GetValue();
    Subsystem->ToolsetRegistry.RegisterToolsetClass(UMyToolset::StaticClass());
    
    // 2. 查询 Schema (AI 会做这一步)
    FString Schema = UToolsetRegistry::GetAllToolsetJsonSchemas();
    UE_LOG(LogTemp, Log, TEXT("Toolset Schemas:\n%s"), *Schema);
    
    // 3. 调用工具 (模拟 AI 调用)
    FString OutResult, OutError;
    UToolsetRegistry::ExecuteTool(
        TEXT("MyToolset"), // 工具集名称 (默认为类名)
        TEXT("Add"),       // 工具名称 (函数名)
        TEXT(R"({"A": 5, "B": 3})"), // JSON 输入
        OutResult,
        OutError
    );
    
    if (OutError.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT("Tool Result: %s"), *OutResult); // 应输出 8
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PythonScriptPlugin` | 为工具集提供 Python 脚本支持，可能用于定义或调用工具。 |
| `EditorScriptingUtilities` | 提供编辑器脚本相关的实用工具函数。 |
| `FileSandbox` | 提供文件沙箱功能，用于安全地执行可能修改文件系统的工具操作。 |

## 维护状态

### 近期更新

- 2026-04-24 0cd2b3ea [Backout] - CL53139837
- 2026-04-24 8dc8f3fd Standardize Epic toolset plugin structure
- 2026-04-24 f45d0c4c Fix possible null deref in AgentSkill::ListSkills when a skill class path can't be loaded.

### 维护评价

ToolsetRegistry 是一个非常新的实验性插件，所有提交记录都集中在同一天（2026-04-24）。从提交信息看，它经历了结构标准化和一些 bug 修复，表明它正处于积极的早期开发阶段。

**优点**：
- 设计目标明确，为 AI 与 UE 集成提供了标准化框架。
- 代码结构清晰，包含了完整的测试用例。
- 依赖于成熟的插件（Python, FileSandbox）。

**风险与注意事项**：
- **实验性**：标记为 `IsExperimentalVersion=true`，API 和功能可能会发生重大变化。
- **默认禁用**：需要手动在插件列表中启用。
- **早期阶段**：虽然代码完整，但缺乏长期维护记录，其稳定性和未来支持存在不确定性。

**推荐**：如果你正在探索 AI 与 UE 编辑器的深度集成，并且愿意承担实验性 API 变化的风险，可以尝试使用。对于生产环境，建议等待其脱离实验状态或进行更长期的观察。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolsetRegistry)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolsetRegistry/Source/ToolsetRegistry/Private/Tests)